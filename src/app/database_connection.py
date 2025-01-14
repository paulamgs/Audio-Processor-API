
import aiosqlite

DB_PATH = "src/database/audio_metadata.db"


async def create_db():
    """
    This method connects to the SQLite database found in DB_PATH and creates a table
    named 'audio_metadata' if it does not already exist.
    The table contains the following fields:
        - session_id: Text, primary key, not null
        - timestamp: Text, not null
        - file_name: Text, not null
        - length_seconds: Real, not null
    """
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.cursor()

        await cursor.execute('''
        CREATE TABLE IF NOT EXISTS audio_metadata (
            session_id TEXT PRIMARY KEY NOT NULL,
            timestamp TEXT NOT NULL,
            file_name TEXT NOT NULL,
            length_seconds REAL NOT NULL
        )
        ''')

        await conn.commit()

async def save_metadata(session_id: str, timestamp: str,
                         file_name: str, length_seconds: float) -> None:
    """
    Saves the audio metadata into the SQLite database.

    Parameters:
        - session_id (str): A unique identifier for the audio session.
        - timestamp (str): ISO-8601 formatted string representing the time of the session.
        - file_name (str): The name of the audio file.
        - length_seconds (float): Duration of the audio file in seconds.

    It handles two types of exceptions:
        - IntegrityError: Raised when the session_id already exists in the table.
        - Error: Raised for any other database-related issues.

    Raises:
        - DatabaseError: Custom exception
    """
    try:
        async with aiosqlite.connect(DB_PATH) as conn:
            await conn.execute('''
            INSERT INTO audio_metadata (session_id, timestamp, file_name, length_seconds)
            VALUES (?, ?, ?, ?)
            ''', (session_id, timestamp, file_name, length_seconds))
            await conn.commit()
    except aiosqlite.IntegrityError as e:
        raise DatabaseError(f"Session ID '{session_id}' already exists. {str(e)}") from e
    except aiosqlite.Error as e:
        raise DatabaseError(f"Could not save metadata: {str(e)}") from e

class DatabaseError(Exception):
    """Custom exception for database-related errors."""
    pass
