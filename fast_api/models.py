# ✅ app/models.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from fast_api.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"))

    organization = relationship("Organization", back_populates="users")
    deployments = relationship("Deployment", back_populates="owner")


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    invite_code = Column(String, unique=True, nullable=False)

    users = relationship("User", back_populates="organization")


class Cluster(Base):
    __tablename__ = "clusters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    total_cpu = Column(Integer)
    total_ram = Column(Integer)
    total_gpu = Column(Integer)

    allocated_cpu = Column(Integer, default=0)
    allocated_ram = Column(Integer, default=0)
    allocated_gpu = Column(Integer, default=0)

    deployments = relationship("Deployment", back_populates="cluster")
    organization_id = Column(Integer, ForeignKey("organizations.id"))

class Deployment(Base):
    __tablename__ = "deployments"

    id = Column(Integer, primary_key=True, index=True)
    docker_image = Column(String, nullable=False)
    required_cpu = Column(Integer)
    required_ram = Column(Integer)
    required_gpu = Column(Integer)
    priority = Column(Integer, default=1)
    status = Column(String, default="queued")

    cluster_id = Column(Integer, ForeignKey("clusters.id"))
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    cluster = relationship("Cluster", back_populates="deployments")
    owner = relationship("User", back_populates="deployments")
