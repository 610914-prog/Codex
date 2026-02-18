from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.azure import AzureDeploymentService
from app.db import create_agent, get_agent, init_db, list_agents, update_agent_status
from app.models import AgentCreate, AgentStatus, DeployRequest

app = FastAPI(title="Azure AI Agent Builder")

BASE_DIR = Path(__file__).resolve().parent.parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
service = AzureDeploymentService()


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "agents": list_agents()})


@app.post("/api/agents")
def create_agent_api(payload: AgentCreate):
    return create_agent(payload)


@app.get("/api/agents")
def list_agents_api():
    return list_agents()


@app.post("/api/agents/{agent_id}/deploy")
def deploy_agent(agent_id: int, payload: DeployRequest):
    agent = get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    result = service.deploy(agent, payload)
    if result.success:
        target = f"{payload.resource_group}/{payload.container_app_name}"
        update_agent_status(agent_id, AgentStatus.deployed, deployment_target=target)
    else:
        update_agent_status(agent_id, AgentStatus.failed)

    return result
