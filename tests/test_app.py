from fastapi.testclient import TestClient
import importlib.util
from pathlib import Path

# Import the app from src.app
spec = importlib.util.spec_from_file_location('app_module', str(Path(__file__).resolve().parents[1] / 'src' / 'app.py'))
app_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_module)
app = app_module.app

client = TestClient(app)


def test_get_activities():
    resp = client.get('/activities')
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # Expect some known activity keys
    assert 'Chess Club' in data


def test_signup_and_duplicate_signup_and_unregister_flow():
    activity = 'Chess Club'
    email = 'pytest-user@mergington.edu'

    # Ensure participant not present initially
    resp = client.get('/activities')
    assert resp.status_code == 200
    participants = resp.json()[activity]['participants']
    if email in participants:
        # remove if leftover from previous runs
        client.delete(f"/activities/{activity}/participants", params={'email': email})

    # Signup successfully
    resp = client.post(f"/activities/{activity}/signup", params={'email': email})
    assert resp.status_code == 200
    assert 'Signed up' in resp.json().get('message', '')

    # Duplicate signup should fail with 400
    resp = client.post(f"/activities/{activity}/signup", params={'email': email})
    assert resp.status_code == 400

    # Unregister successfully
    resp = client.delete(f"/activities/{activity}/participants", params={'email': email})
    assert resp.status_code == 200
    assert 'Unregistered' in resp.json().get('message', '')

    # Unregistering again should return 404
    resp = client.delete(f"/activities/{activity}/participants", params={'email': email})
    assert resp.status_code == 404
