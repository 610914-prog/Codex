const agentForm = document.getElementById('agent-form');
const deployForm = document.getElementById('deploy-form');
const agentsPre = document.getElementById('agents');
const resultPre = document.getElementById('result');
const refreshBtn = document.getElementById('refresh');

async function fetchAgents() {
  const res = await fetch('/api/agents');
  const data = await res.json();
  agentsPre.textContent = JSON.stringify(data, null, 2);
}

agentForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const form = new FormData(agentForm);
  const payload = {
    name: form.get('name'),
    model: form.get('model'),
    system_prompt: form.get('system_prompt')
  };

  const res = await fetch('/api/agents', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(payload)
  });
  const data = await res.json();
  resultPre.textContent = JSON.stringify(data, null, 2);
  fetchAgents();
});

deployForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const form = new FormData(deployForm);
  const agentId = form.get('agent_id');
  const payload = {
    resource_group: form.get('resource_group'),
    location: form.get('location'),
    container_app_environment: form.get('container_app_environment'),
    container_app_name: form.get('container_app_name'),
    image_name: form.get('image_name'),
    dry_run: form.get('dry_run') === 'on'
  };

  const res = await fetch(`/api/agents/${agentId}/deploy`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(payload)
  });
  const data = await res.json();
  resultPre.textContent = JSON.stringify(data, null, 2);
  fetchAgents();
});

refreshBtn.addEventListener('click', fetchAgents);
fetchAgents();
