"""
Example to show sending message(s) to a Service Bus Queue.
"""

import os
from azure.servicebus import ServiceBusClient, ServiceBusMessage, ServiceBusSubQueue


CONNECTION_STR = os.environ['SERVICEBUS_CONNECTION_STR']
# QUEUE_NAME = os.environ["SERVICEBUS_QUEUE_NAME"]
RETRY_MAX = 3

# queues_list = [
#     'cnv-debug-test',
#     'cnv-debug-test-2'
# ]

queues_list = [
    'conversion-entity-accounting',
    'conversion-entity-accounting-enriched-analyzer',
    'conversion-entity-management',
    'conversion-entity-management-enriched-entity-analyzer',
    'conversion-entity-management-failed-publishing',
    'conversion-forms',
    'conversion-forms-enriched-analyzer'
]


def clear_queue(client, queue_name):
    retry = 0
    print('connecting to queue: ', queue_name)
    receiver = client.get_queue_receiver(queue_name=queue_name)
    with receiver:
        while(True):
            received_msgs = receiver.receive_messages(max_message_count=50, max_wait_time=5)
            if len(received_msgs) == 0:
                retry += 1
                print(f"verifying....({retry})")
                if retry > RETRY_MAX:
                    return
                
            print('Found (', len(received_msgs), ') message(s) in queue')
            for msg in received_msgs:
                receiver.complete_message(msg)

def clear_deadletter_queue(client, queue_name):
    retry = 0
    dlq_receiver  = client.get_queue_receiver(queue_name=queue_name, sub_queue=ServiceBusSubQueue.DEAD_LETTER)
    with dlq_receiver :
        while(True):
            received_msgs = dlq_receiver .receive_messages(max_message_count=50, max_wait_time=5)
            if len(received_msgs) == 0:
                retry += 1
                print(f"retrying....({retry})")
                if retry > RETRY_MAX:
                    return

            print('Found (', len(received_msgs), ') message(s) in DLQ queue')
            for msg in received_msgs:
                dlq_receiver .complete_message(msg)

servicebus_client = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR)
with servicebus_client:
    for queue in queues_list:
        clear_queue(servicebus_client, queue)
        clear_deadletter_queue(servicebus_client, queue)

print("Receive is done.")