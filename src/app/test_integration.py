import base64
import os
import shutil
import tempfile
from unittest.mock import patch

import numpy as np
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

from app.database_connection import create_db
from main import app


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_db():
    """Set up a temporary database for testing."""
    temp_dir = tempfile.mkdtemp()
    temp_db_path = os.path.join(temp_dir, "test_database.db")

    with patch("app.database_connection.DB_PATH", temp_db_path):
        await create_db()

        yield

    # Cleanup: Delete the temporary directory and database
    shutil.rmtree(temp_dir)

@pytest.fixture
def client():
    """Fixture for creating a TestClient."""
    return TestClient(app)

def generate_sample_audio():
    """Generate a sample base64-encoded audio file for testing."""

    sample_rate = 4000
    duration_seconds = 7
    num_samples = sample_rate * duration_seconds

    audio_data = np.random.randint(low=-32768, high=32767, size=num_samples, dtype=np.int16)
    audio_bytes = audio_data.tobytes()
    encoded_audio = base64.b64encode(audio_bytes).decode('utf-8')
    return encoded_audio

def generate_audio_request():
    encoded_audio = generate_sample_audio()

    audio_request = {
        "session_id": "abc123",
        "timestamp": "2025-01-13T12:00:00Z",
        "audio_files": [
            {
                "file_name": "audio.raw",
                "encoded_audio": encoded_audio
            }
        ]
    }
    return audio_request

@pytest.mark.asyncio(loop_scope="function")
async def test_process_audio_success(client):
    """Integration test for the /process-audio endpoint."""

    valid_audio_request = generate_audio_request()
    response = client.post("/process-audio", json=valid_audio_request)

    assert response.status_code == 200
    response_json = response.json()
    assert response_json['status'] == 'success'

@pytest.mark.asyncio
async def test_process_audio_missing_session_id(client):
    encoded_audio = generate_sample_audio()

    audio_request = {
        "timestamp": "2025-01-13T12:00:00Z",
        "audio_files": [
            {
                "file_name": "audio.raw",
                "encoded_audio": encoded_audio
            }
        ]
    }

    response = client.post("/process-audio", json=audio_request)

    assert response.status_code == 422 # 422 Unprocessable Entity

@pytest.mark.asyncio
async def test_process_audio_invalid_session_id(client):
    encoded_audio = generate_sample_audio()

    audio_request = {
        "session_id": "@@2!!",
        "timestamp": "2025-01-13T12:00:00Z",
        "audio_files": [
            {
                "file_name": "audio.raw",
                "encoded_audio": encoded_audio
            }
        ]
    }

    response = client.post("/process-audio", json=audio_request)

    assert response.status_code == 422 # Unprocessable Entity
    response_json = response.json()
    assert response_json["detail"][0]["msg"] == "Value error, Session ID must be alphanumeric."


@pytest.mark.asyncio
async def test_process_audio_duplicated_session_id(client):
    valid_audio_request = generate_audio_request()

    # First request with a valid session_id
    response = client.post("/process-audio", json=valid_audio_request)

    # Assert that the first response status is 'success'
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['status'] == 'success'


    # Second request with the same session_id
    response2 = client.post("/process-audio", json=valid_audio_request)

    # Assert that the second response status is 'error' due to duplicate session_id
    assert response2.status_code == 200
    response2_json = response2.json()
    assert response2_json['status'] == 'error'
    session_id = valid_audio_request['session_id']
    expected_message = f"Session ID '{session_id}' already exists."
    assert expected_message in response2_json['message']

@pytest.mark.asyncio
async def test_process_audio_missing_audio_files(client):
    audio_request = {
        "session_id": "abc123",
        "timestamp": "2025-01-13T12:00:00Z",
        "audio_files": []  # Empty list of audio files
    }

    response = client.post("/process-audio", json=audio_request)
    assert response.status_code == 422 # Unprocessable Entity

    response_json = response.json()
    assert response_json["detail"][0]["msg"] == "Value error, audio_files must not be empty"

@pytest.mark.asyncio
async def test_process_audio_invalid_base64(client):
    audio_request = {
        "session_id": "abc123",
        "timestamp": "2025-01-13T12:00:00Z",
        "audio_files": [
            {
                "file_name": "audio.raw",
                "encoded_audio": "invalid_base64_string!"  # Invalid base64 string
            }
        ]
    }

    response = client.post("/process-audio", json=audio_request)
    assert response.status_code == 422
    response_json = response.json()
    assert response_json["detail"][0]["msg"] == "Value error, Invalid Base64-encoded audio data"

@pytest.mark.asyncio
async def test_process_audio_invalid_timestamp_format(client):
    audio_request = {
        "session_id": "abc123",
        "timestamp": "2025-01-13T25:00:00",
        "audio_files": [
            {
                "file_name": "audio.raw",
                "encoded_audio": generate_sample_audio()
            }
        ]
    }

    response = client.post("/process-audio", json=audio_request)

    assert response.status_code == 422
    response_json = response.json()
    assert response_json["detail"][0]["msg"] == "Value error, Timestamp must be in ISO-8601 format."