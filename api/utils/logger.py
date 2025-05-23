from datetime import datetime
from api.db.database import Database


async def log_usage(
    user_id: int | None, action: str, status: str, error_message: str | None = None
):
    query = """
        INSERT INTO usage_logs (user_id, action, status, error_message, created_at)
        VALUES (%s, %s, %s, %s, %s)
    """
    await Database.execute(
        query, user_id, action, status, error_message, datetime.now()
    )
