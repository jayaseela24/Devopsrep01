import asyncio
from azure.servicebus.aio import ServiceBusClient

NAMESPACE_CONNECTION_STR = "Endpoint=sb://revx-msl-service-bus-ref.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=FdE7xKGWKhcdKX0Dl1mUxun1wGJzJCITk+ASbNuYdXY="
QUEUE_NAME = "conversion-entity-accounting"


async def run():
    # create a Service Bus client using the connection string
    async with ServiceBusClient.from_connection_string(
        conn_str=NAMESPACE_CONNECTION_STR,
        logging_enable=True) as servicebus_client:

        async with servicebus_client:
            # get the Queue Receiver object for the queue
            print("connecting to queue: ", QUEUE_NAME)
            receiver = servicebus_client.get_queue_receiver(queue_name=QUEUE_NAME)
            async with receiver:
                print("receiving messages...")
                received_msgs = await receiver.receive_messages(max_wait_time=90, max_message_count=1)
                for msg in received_msgs:
                    print("Received: " + str(msg))
                    # complete the message so that the message is removed from the queue
                    await receiver.complete_message(msg)


asyncio.run(run())