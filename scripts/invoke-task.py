from celery import Celery
import os
from datetime import datetime

now = datetime.now()
timestamp = now.strftime("%Y%m%d%H%M")
job_ticket_id = f"{timestamp}_rabbitmq_email_notifier"

app1 = Celery('tasks')
app1.config_from_object('celeryconfig')

arguments = {"subject": "test subject",
             "body": "test message",
             "receipients": "chip_goines@harvard.edu"}

res = app1.send_task('rabbitmq-email-notifier.tasks.notify_email_message',
                     args=[arguments], kwargs={},
                     queue=os.getenv("CONSUME_QUEUE_NAME"))
