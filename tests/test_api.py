from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_create_list_and_deploy_agent_dry_run():
    create_response = client.post(
        "/api/agents",
        json={
            "name": "Test Agent",
            "model": "gpt-4o-mini",
            "system_prompt": "You help users deploy to Azure safely.",
        },
    )
    assert create_response.status_code == 200
    agent = create_response.json()
    assert agent["name"] == "Test Agent"

    list_response = client.get("/api/agents")
    assert list_response.status_code == 200
    assert len(list_response.json()) >= 1

    deploy_response = client.post(
        f"/api/agents/{agent['id']}/deploy",
        json={
            "resource_group": "rg-test",
            "location": "eastus",
            "container_app_environment": "env-test",
            "container_app_name": "agent-test",
            "image_name": "myacr.azurecr.io/agent:latest",
            "dry_run": True,
        },
    )
    assert deploy_response.status_code == 200
    result = deploy_response.json()
    assert result["success"] is True
    assert "az containerapp create" in result["command"]
