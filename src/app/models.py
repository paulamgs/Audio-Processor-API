
import base64
from datetime import datetime

from pydantic import BaseModel, Field, RootModel, field_validator, model_validator


class AudioFile(BaseModel):
    file_name: str = Field(..., description="Name of the audio file")
    encoded_audio: str = Field(..., description="Base64-encoded audio data")

    @model_validator(mode="after")
    def validate_base64_audio(cls, value):
        try:
            decoded_audio = base64.b64decode(value.encoded_audio)
            if len(decoded_audio) == 0:
                raise ValueError("Decoded audio file is empty")
        except Exception:
            raise ValueError("Invalid Base64-encoded audio data") from None
        return value

class AudioRequest(BaseModel):
    session_id: str = Field(..., description="Unique identifier for the session")
    timestamp: datetime = Field(..., description="Timestamp in ISO-8601 format")
    audio_files: list[AudioFile] = Field(..., description="List of audio files")

    @field_validator("session_id", mode="after")
    def validate_session_id(cls, value):
        if not value.isalnum():
            raise ValueError("Session ID must be alphanumeric.")
        return value

    @field_validator("timestamp", mode="before")
    def validate_timestamp(cls, value):
        if isinstance(value, str):
            try:
                datetime.fromisoformat(value)
            except ValueError:
                raise ValueError("Timestamp must be in ISO-8601 format.") from None
        return value

    @model_validator(mode="after")
    def validate_audio_files(cls, values):
        if not values.audio_files:
            raise ValueError("audio_files must not be empty")
        return values

class ProcessedFile(BaseModel):
    file_name: str = Field(..., description="Name of the audio file")
    length_seconds: float = Field(..., description="Length of the audio file in seconds")

class SuccessResponse(BaseModel):
    status: str = Field("success", description="Indicates successful processing")
    processed_files: list[ProcessedFile] = Field(..., description="List of successfully processed files")

class ErrorResponse(BaseModel):
    status: str = Field("error", description="Indicates an error occurred")
    message: str = Field(..., description="Error message describing the failure")

class ResponseModel(RootModel):
    root: SuccessResponse | ErrorResponse


