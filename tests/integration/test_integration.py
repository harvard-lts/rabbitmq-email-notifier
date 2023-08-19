from celery import Celery
import os
import pika

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
        print(str(body))
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
