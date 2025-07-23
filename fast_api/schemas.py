from pydantic import BaseModel
from typing import Optional
from pydantic import Field

# ----- User Schemas -----


class UserResponse(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True

# ----- Organization Schemas -----

class OrganizationCreate(BaseModel):
    name: str
    invite_code: str

class OrganizationResponse(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

# ----- Cluster Schemas -----

class ClusterCreate(BaseModel):
    name: str
    total_cpu: int
    total_ram: int
    total_gpu: int

class ClusterResponse(BaseModel):
    id: int
    name: str
    total_cpu: int
    total_ram: int
    total_gpu: int
    allocated_cpu: int
    allocated_ram: int
    allocated_gpu: int

    class Config:
        orm_mode = True

# ----- Deployment Schemas -----

class DeploymentCreate(BaseModel):
    docker_image: str
    total_cpu: int
    total_ram: int
    total_gpu: int
    priority: Optional[int] = Field(default=1, ge=1)
    cluster_id: int

class DeploymentResponse(BaseModel):
    id: int
    docker_image: str
    status: str
    cluster_id: int
    priority: int

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    username: str
    password: str
    invite_code: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None