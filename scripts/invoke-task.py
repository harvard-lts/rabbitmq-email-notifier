from celery import Celery
import os
from datetime import datetime

now = datetime.now()
timestamp = now.strftime("%Y%m%d%H%M")
job_ticket_id = f"{timestamp}_rabbitmq_email_notifier"

app1 = Celery()
app1.config_from_object('celeryconfig')

arguments = {"subject": "test subject",
             "body": "test message",
             "recipients": "chip_goines@harvard.edu"}
NOTIFIER_TASK_NAME = os.getenv("NOTIFIER_TASK_NAME",
                               "rabbitmq-email-notifier." +
                               "tasks.notify_email_message")
res = app1.send_task(NOTIFIER_TASK_NAME, args=[arguments], kwargs={},
                     queue=os.getenv("CONSUME_QUEUE_NAME"))
