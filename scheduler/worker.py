import asyncio
import json
import aio_pika
from sqlalchemy.orm import Session
from fast_api.db import SessionLocal
from fast_api.models import Deployment, Cluster

RABBITMQ_URL = "amqp://guest:guest@rabbitmq/"

async def process_message(message: aio_pika.IncomingMessage):
    async with message.process():
        payload = json.loads(message.body)
        db: Session = SessionLocal()

        deployment_id = payload["deployment_id"]
        deployment = db.query(Deployment).filter(Deployment.id == deployment_id).first()
        cluster = db.query(Cluster).filter(Cluster.id == deployment.cluster_id).first()

        # Try to allocate resources
        enough = (
            cluster.allocated_cpu + deployment.required_cpu <= cluster.total_cpu and
            cluster.allocated_ram + deployment.required_ram <= cluster.total_ram and
            cluster.allocated_gpu + deployment.required_gpu <= cluster.total_gpu
        )

        if enough:
            deployment.status = "running"
            cluster.allocated_cpu += deployment.required_cpu
            cluster.allocated_ram += deployment.required_ram
            cluster.allocated_gpu += deployment.required_gpu
            print(f"Started deployment {deployment.id}")
        else:
            # Preemption logic: Find lower priority deployment to remove
            lower_priority = db.query(Deployment)\
                .filter(Deployment.cluster_id == cluster.id, Deployment.status == "running")\
                .filter(Deployment.priority < deployment.priority)\
                .order_by(Deployment.priority.asc())\
                .first()

            if lower_priority:
                # Free its resources
                cluster.allocated_cpu -= lower_priority.required_cpu
                cluster.allocated_ram -= lower_priority.required_ram
                cluster.allocated_gpu -= lower_priority.required_gpu
                lower_priority.status = "preempted"

                # Allocate for new high-priority deployment
                deployment.status = "running"
                cluster.allocated_cpu += deployment.required_cpu
                cluster.allocated_ram += deployment.required_ram
                cluster.allocated_gpu += deployment.required_gpu
                print(f"Preempted deployment {lower_priority.id} for {deployment.id}")
            else:
                deployment.status = "queued"
                print(f"Queued deployment {deployment.id} (not enough resources)")

        db.commit()
        db.close()

async def main():
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    channel = await connection.channel()
    queue = await channel.declare_queue("deployments", durable=True)
    await queue.consume(process_message, no_ack=False)
    print("Scheduler is running...")
    return connection

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    connection = loop.run_until_complete(main())
    try:
        loop.run_forever()
    finally:
        loop.run_until_complete(connection.close())
