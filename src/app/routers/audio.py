
import base64

import numpy as np
from fastapi import APIRouter

from app.database_connection import DatabaseError, save_metadata
from app.models import (
    AudioRequest,
    ErrorResponse,
    ProcessedFile,
    ResponseModel,
    SuccessResponse,
)

router = APIRouter()

@router.post("/process-audio", response_model=ResponseModel)
async def process_audio(audio_request: AudioRequest):

    processed_files = []
    for audio_file in audio_request.audio_files:
        try:
            decoded_audio = decode_audio(audio_file.encoded_audio)
            audio_samples = np.frombuffer(decoded_audio, dtype=np.int16)
            audio_length = calculate_audio_length(audio_samples)
        except ValueError as e:
            return ErrorResponse(message=str(e))

        try:
            await save_metadata(audio_request.session_id,
                                audio_request.timestamp,
                                audio_file.file_name,
                                audio_length)
        except DatabaseError as e:
            return ErrorResponse(message=str(e))

        processed_file = ProcessedFile(file_name=audio_file.file_name,
                                       length_seconds=audio_length)
        processed_files.append(processed_file)

    return SuccessResponse(processed_files=processed_files)


def align_to_int16(data: bytes) -> bytes:
    """
    Adds extra padding to ensure the byte length of decoded audio
    is a multiple of 2 to comply with the int16 audio format.

    Args:
        data (bytes): The decoded audio byte data.

    Returns:
        bytes: The aligned audio data.
    """
    if len(data) % 2 != 0:
        data += b'\x00'
    return data

def decode_audio(encoded_audio: str) -> bytes:
    """
    Decodes a Base64-encoded audio file and calls a function to align data to int16.

    Args:
        audio_file (AudioFile): An object containing file name and encoded audio data.

    Returns:
        bytes: Decoded audio data as bytes.

    Raises:
        ValueError: If the decoded audio length is not compatible with int16 format.
    """
    try:
        decoded_audio = base64.b64decode(encoded_audio)
        return align_to_int16(decoded_audio)
    except (base64.binascii.Error, ValueError) as e:
        raise ValueError("Invalid Base64-encoded audio data") from e

def calculate_audio_length(raw_audio: np.ndarray, sample_rate: float = 4000) -> float:
    """
    Calculates the duration of audio in seconds based on sample rate.

    Args:
        raw_audio (np.ndarray): The raw audio data as a NumPy array.
        sample_rate (float): The sample rate of the audio in Hz. Defaults to 4000 Hz.

    Returns:
        float: The length of the audio in seconds.

    Raises:
        ValueError: Audio data type is not int16.
    """
    if raw_audio.dtype != np.int16:
        raise ValueError("Audio data must be of type int16")

    length_seconds = len(raw_audio) / sample_rate

    if not isinstance(sample_rate, int) or sample_rate <= 0:
        raise ValueError("sample_rate must be a positive integer.")
    if length_seconds <= 0:
        raise ValueError("Calculated audio length in seconds must be greater than 0.")
    return length_seconds


