"""
Example to show sending message(s) to a Service Bus Queue.
"""

import os
from azure.servicebus import ServiceBusClient, ServiceBusMessage


CONNECTION_STR = os.environ['SERVICEBUS_CONNECTION_STR']
QUEUE_NAME = os.environ["SERVICEBUS_QUEUE_NAME"]

servicebus_client = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR, logging_enable=True)
with servicebus_client:
    receiver = servicebus_client.get_queue_receiver(queue_name=QUEUE_NAME)
    with receiver:
        received_msgs = receiver.receive_messages(max_message_count=1000, max_wait_time=5)
        for msg in received_msgs:
            print(str(msg))
            receiver.dead_letter_message(msg)

print("Send message is done.")