import json
import aio_pika

RABBITMQ_URL = "amqp://guest:guest@rabbitmq/"

async def enqueue_deployment(payload: dict):
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    channel = await connection.channel()
    queue = await channel.declare_queue("deployments", durable=True)

    await channel.default_exchange.publish(
        aio_pika.Message(body=json.dumps(payload).encode()),
        routing_key=queue.name,
    )
    await connection.close()
