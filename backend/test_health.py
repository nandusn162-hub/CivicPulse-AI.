from fastapi.testclient import TestClient
from app.main import app
print(TestClient(app).get('/api/v1/health').json())