from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class AgentStatus(str, Enum):
    draft = "draft"
    deployed = "deployed"
    failed = "failed"


class AgentCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    system_prompt: str = Field(min_length=10, max_length=8000)
    model: str = Field(default="gpt-4o-mini", min_length=2, max_length=100)


class Agent(BaseModel):
    id: int
    name: str
    system_prompt: str
    model: str
    status: AgentStatus
    deployment_target: Optional[str] = None
    created_at: datetime


class DeployRequest(BaseModel):
    image_name: str = Field(default="myacr.azurecr.io/azure-agent:latest", min_length=5)
    resource_group: str = Field(min_length=2)
    location: str = Field(default="eastus", min_length=3)
    container_app_environment: str = Field(min_length=2)
    container_app_name: str = Field(min_length=2)
    dry_run: bool = True


class DeployResult(BaseModel):
    success: bool
    message: str
    command: Optional[str] = None
