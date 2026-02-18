from __future__ import annotations

import os
import shlex
import subprocess
from dataclasses import dataclass

from app.models import Agent, DeployRequest, DeployResult


@dataclass
class AzureConfig:
    endpoint: str | None
    api_key: str | None
    api_version: str

    @classmethod
    def from_env(cls) -> "AzureConfig":
        return cls(
            endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview"),
        )


class AzureDeploymentService:
    def deploy(self, agent: Agent, request: DeployRequest) -> DeployResult:
        command = self._build_command(agent, request)
        if request.dry_run:
            return DeployResult(
                success=True,
                message="Dry run successful. Execute the generated Azure CLI command to deploy.",
                command=command,
            )

        completed = subprocess.run(command, shell=True, capture_output=True, text=True)
        if completed.returncode != 0:
            return DeployResult(success=False, message=completed.stderr.strip() or "Deployment failed", command=command)

        return DeployResult(success=True, message=completed.stdout.strip() or "Deployment succeeded", command=command)

    def _build_command(self, agent: Agent, request: DeployRequest) -> str:
        env_vars = {
            "AGENT_NAME": agent.name,
            "AGENT_MODEL": agent.model,
            "AGENT_SYSTEM_PROMPT": agent.system_prompt,
        }
        env_args = " ".join(
            f"{k}={shlex.quote(v)}" for k, v in env_vars.items()
        )

        return (
            "az containerapp create "
            f"--name {shlex.quote(request.container_app_name)} "
            f"--resource-group {shlex.quote(request.resource_group)} "
            f"--environment {shlex.quote(request.container_app_environment)} "
            f"--location {shlex.quote(request.location)} "
            f"--image {shlex.quote(request.image_name)} "
            f"--env-vars {env_args}"
        )
