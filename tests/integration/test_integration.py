from celery import Celery
import os
import pika
import json

app1 = Celery('tasks')
app1.config_from_object('celeryconfig')


def retrieve_from_queue():
    queue = os.getenv("NEXT_QUEUE_NAME", "dead-letter")
    parameters = pika.URLParameters(os.getenv("BROKER_URL"))
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    method_frame, header_frame, body = channel.basic_get(queue=queue)
    if method_frame.NAME == 'Basic.GetEmpty':
        connection.close()
        return False
    else:
        channel.basic_ack(delivery_tag=method_frame.delivery_tag)
        connection.close()
        json_str = body.decode(encoding='UTF-8')
        json_data = (json.loads(json_str))[0][0]
        if "subject" in json_data:
            if json_data["subject"] != "test subject":
                return False
        if "body" in json_data:
            if json_data["body"] != "test message":
                return False
        if "recipients" in json_data:
            if json_data["recipients"] != "john_harvard@harvard.edu":
                return False
        return True


class TestNotifierIntegrationClass():

    def test_notifier(self):
        arguments = {"subject": "test subject",
                     "body": "test message",
                     "recipients": "john_harvard@harvard.edu"}

        # send msg to queue
        app1.send_task('rabbitmq-email-notifier.tasks.notify_email_message',
                       args=[arguments], kwargs={},
                       queue=os.getenv("CONSUME_QUEUE_NAME", "email-notifier"))

        assert retrieve_from_queue()
