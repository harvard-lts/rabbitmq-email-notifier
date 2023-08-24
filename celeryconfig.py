import os

broker_url = os.getenv('BROKER_URL')
task_serializer = 'json'
accept_content = ['application/json']
result_serializer = 'json'
timezone = 'US/Eastern'
enable_utc = True
worker_enable_remote_control = False
NOTIFIER_TASK_NAME = os.getenv("NOTIFIER_TASK_NAME",
                               "rabbitmq-email-notifier." +
                               "tasks.notify_email_message")
task_routes = {
    NOTIFIER_TASK_NAME:
    {'queue': os.getenv("CONSUME_QUEUE_NAME", "email-notifier")}
}
