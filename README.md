# Azure AI Agent Builder

A lightweight FastAPI app to:

1. Create AI agent definitions (name, model, system prompt).
2. Persist them locally in SQLite.
3. Generate or execute Azure Container Apps deployment commands for each agent.

## Features

- Web UI for creating and deploying agents.
- REST API endpoints for automation.
- Dry-run deployment mode that outputs Azure CLI command.
- Basic automated test coverage with `pytest`.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Open: <http://localhost:8000>

## API

- `POST /api/agents`
- `GET /api/agents`
- `POST /api/agents/{agent_id}/deploy`

## Azure deployment notes

This app deploys an existing container image to Azure Container Apps via Azure CLI:

```bash
az login
az extension add --name containerapp
```

Set `dry_run=false` in deploy request to actually execute the command.
