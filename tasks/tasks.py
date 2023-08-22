from celery import Celery
from celery import bootsteps
from celery.signals import worker_ready
from celery.signals import worker_shutdown
from pathlib import Path
import os
import logging
import rabbitmqresources
import json
import traceback
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
        OTLPSpanExporter)
from opentelemetry.sdk.resources import SERVICE_NAME
from opentelemetry.trace.propagation.tracecontext \
    import TraceContextTextMapPropagator

app = Celery()
app.config_from_object('celeryconfig')
rabbitmqresources.configure_logger()
logger = logging.getLogger('rabbitmq-email-notifier')

# tracing setup
JAEGER_NAME = os.getenv('JAEGER_NAME')
JAEGER_SERVICE_NAME = os.getenv('JAEGER_SERVICE_NAME')

resource = Resource(attributes={SERVICE_NAME: JAEGER_SERVICE_NAME})
provider = TracerProvider(resource=resource)
otlp_exporter = OTLPSpanExporter(endpoint=JAEGER_NAME, insecure=True)
span_processor = BatchSpanProcessor(otlp_exporter)
provider.add_span_processor(span_processor)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)


# heartbeat setup
# code is from
# https://github.com/celery/celery/issues/4079#issuecomment-1270085680
hbeat_path = os.getenv("HEARTBEAT_FILE", "/tmp/worker_heartbeat")
ready_path = os.getenv("READINESS_FILE", "/tmp/worker_ready")
update_interval = float(os.getenv("HEALTHCHECK_UPDATE_INTERVAL", 15.0))
HEARTBEAT_FILE = Path(hbeat_path)
READINESS_FILE = Path(ready_path)
UPDATE_INTERVAL = update_interval  # touch file every 15 seconds


class LivenessProbe(bootsteps.StartStopStep):
    requires = {'celery.worker.components:Timer'}

    def __init__(self, worker, **kwargs):  # pragma: no cover
        self.requests = []
        self.tref = None

    def start(self, worker):  # pragma: no cover
        self.tref = worker.timer.call_repeatedly(
            UPDATE_INTERVAL, self.update_heartbeat_file,
            (worker,), priority=10,
        )

    def stop(self, worker):  # pragma: no cover
        HEARTBEAT_FILE.unlink(missing_ok=True)

    def update_heartbeat_file(self, worker):  # pragma: no cover
        HEARTBEAT_FILE.touch()


@worker_ready.connect
def worker_ready(**_):  # pragma: no cover
    READINESS_FILE.touch()


@worker_shutdown.connect
def worker_shutdown(**_):  # pragma: no cover
    READINESS_FILE.unlink(missing_ok=True)


# return the number of seconds this message should expire in the future
def _get_expiration():
    # Default to one hour from now
    expiration = int(os.getenv('MESSAGE_EXPIRATION_SECS', 3600))
    return expiration


app.steps["worker"].add(LivenessProbe)


@app.task(serializer='json',
          name='rabbitmq-email-notifier.tasks.notify_email_message')
def notify_email_message(json_message):
    ctx = None
    if "traceparent" in json_message:  # pragma: no cover, tracing is not being tested # noqa: E501
        carrier = {"traceparent": json_message["traceparent"]}
        ctx = TraceContextTextMapPropagator().extract(carrier)
    with tracer.start_as_current_span("notify_email_message",
                                      context=ctx) as current_span:
        logger.info("message")
        logger.info(json_message)
        current_span.add_event(json.dumps(json_message))

        NEXT_TASK = os.getenv('NEXT_TASK')
        NEXT_QUEUE = os.getenv('NEXT_QUEUE_NAME')
        expiration = _get_expiration()

        body = json_message["body"]
        subject = json_message["subject"]
        recipients = json_message["recipients"]

        if (("exception" in json_message) and
                (json_message["exception"] is not None)):
            exc = traceback.format_exc(json_message["exception"])
            body = body + "\n\n" + exc

        msg_json = {
            "subject": subject,
            "body": body,
            "recipients": recipients
        }

        logger.debug("msg json:")
        logger.debug(msg_json)
        message = json.dumps(msg_json)
        current_span.add_event(message)

        # If only unit testing, return the message and
        # do not trigger the next task.
        if "unit_test" in json_message:
            return msg_json
        # preserve trace id across components
        carrier = {}  # pragma: no cover, tracing is not being tested # noqa: E501
        TraceContextTextMapPropagator().inject(carrier)  # pragma: no cover, tracing is not being tested # noqa: E501
        traceparent = carrier["traceparent"]  # pragma: no cover, tracing is not being tested # noqa: E501
        msg_json["traceparent"] = traceparent  # pragma: no cover, tracing is not being tested # noqa: E501
        current_span.add_event("to next queue")  # pragma: no cover, unit tests end before this span # noqa: E501
        logger.debug("MESSAGE TO QUEUE " + NEXT_QUEUE)
        logger.debug(message)
        app.send_task(NEXT_TASK,
                      args=[msg_json], kwargs={}, expires=expiration,
                      queue=NEXT_QUEUE)  # pragma: no cover, unit tests should not progress the message # noqa: E501
