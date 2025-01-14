# IoT Audio Processing API

## Overview
The IoT Audio Processing API provides functionality to process audio files.
Users can upload audio files, which are validated, decoded, and processed.
Metadata including the audio file name and the audio length is saved in a database.

## Prerequisites
- **Python 3.9+** or **Docker** (for containerized setup)
- **FastAPI** and **Uvicorn** for running the API
- **SQLite** database for storing metadata

## Setup options

### 1. Using DevContainers (Recommended)
The project comes with a **DevContainer** configuration for easy setup and development. To set up the environment using DevContainers:

- Install Visual Studio Code with the **Remote - Containers** extension.
- Open the project folder in VS Code.
- Click on **Reopen in Container** to automatically build the container and install dependencies using the **Dockerfile** and **`pyproject.toml`**.

### 2. Using Dockerfile and `pyproject.toml`
If you're not using DevContainers, you can set up the project using Docker:

- **Dockerfile**: The Dockerfile installs the necessary dependencies and starts the FastAPI app.
- **`pyproject.toml`**: This file defines project dependencies.


### 3. Running the API

Once the environment is set up, run the FastAPI application with the following command:

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## API Endpoints

### POST /process-audio
This endpoint processes a list of audio files. Each audio file is validated, decoded, and its length is calculated. Metadata is then stored in the database.

#### Request Body:
Example of a valid JSON payload to send:

```json
{
  "session_id": "abc123",  
  "timestamp": "2025-01-13T12:00:00Z",  
  "audio_files": [
    {
      "file_name": "audio.raw",  
      "encoded_audio": "UklGRiQARRRRVZFZm10IBAAAAAA...=="
    }
  ]
}
```

- `session_id`: A unique identifier for the session (alphanumeric).
- `timestamp`: The timestamp in ISO-8601 format.
- `audio_files`: A list of audio files to process.
    - `file_name`: Name of the audio file (supports `.raw` files).
    - `encoded_audio`: Base64-encoded audio data.

#### Response:

**Success Response**:
```json
{
  "status": "success",
  "processed_files": [
    {
      "file_name": "audio.raw",
      "length_seconds": 12.34
    }
  ]
}
```
- `status`: Indicates that the request was successful.
- `processed_files`: A list of processed files with their name and length (in seconds).

**Error Response**:
```json
{
  "status": "error",
  "message": "Invalid Base64-encoded audio data"
}
```

- `status`: Indicates that an error occurred.
- `message`: Describes the error.

### Example Use Cases

#### Successful Example:
**Request**:
```json
{
  "session_id": "abc123",  
  "timestamp": "2025-01-13T12:00:00Z",  
  "audio_files": [
    {
      "file_name": "audio.raw",  
      "encoded_audio": "UklGRiQAAABXQVZFZm10IBAAAAAA...=="
    }
  ]
}
```

**Response**:
```json
{
  "status": "success",
  "processed_files": [
    {
      "file_name": "audio.raw",
      "length_seconds": 12.34
    }
  ]
}
```

## Database

The application uses **SQLite** for storing audio metadata. The `audio_metadata` table contains the following columns:
- `session_id`: The session ID (string).
- `timestamp`: Timestamp of the request (datetime).
- `file_name`: The name of the processed audio file (string).
- `length_seconds`: The length of the audio file in seconds (float).

## License

MIT License.
