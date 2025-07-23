from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fast_api.db import get_db
from fast_api.models import Cluster, Deployment, User
from fast_api.schemas import ClusterCreate, DeploymentCreate
from fast_api.auth import get_current_user
from scheduler.enque import enqueue_deployment

router = APIRouter()

@router.post("/clusters/create")
async def create_cluster(cluster: ClusterCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_cluster = Cluster(
        name=cluster.name,
        total_ram=cluster.total_ram,
        total_cpu=cluster.total_cpu,
        total_gpu=cluster.total_gpu,
        organization_id=current_user.organization_id,
        allocated_ram=0,
        allocated_cpu=0,
        allocated_gpu=0
    )
    db.add(new_cluster)
    db.commit()
    db.refresh(new_cluster)
    return {"msg": "Cluster created", "cluster": new_cluster}

@router.post("/deployments/create")
async def create_deployment(deployment: DeploymentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cluster = db.query(Cluster).filter_by(id=deployment.cluster_id, organization_id=current_user.organization_id).first()
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")

    # Check if resources are available
    if (cluster.allocated_ram + deployment.total_ram <= cluster.total_ram and
        cluster.allocated_cpu + deployment.total_cpu <= cluster.total_cpu and
        cluster.allocated_gpu + deployment.total_gpu <= cluster.total_gpu):

        # Allocate resources
        cluster.allocated_ram += deployment.total_ram
        cluster.allocated_cpu += deployment.total_cpu
        cluster.allocated_gpu += deployment.total_gpu

        status = "running"
    else:
        status = "queued"

    new_deployment = Deployment(
        owner_id=current_user.id,
        cluster_id=deployment.cluster_id,
        docker_image=deployment.docker_image,
        required_ram=deployment.total_ram,
        required_cpu=deployment.total_cpu,
        required_gpu=deployment.total_gpu,
        priority=deployment.priority,
        status=status
    )
    db.add(new_deployment)
    db.commit()
    db.refresh(new_deployment)
    await enqueue_deployment({"deployment_id": new_deployment.id})
    return {"msg": "Deployment created", "deployment": new_deployment}
