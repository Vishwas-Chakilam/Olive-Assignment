from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection


async def run_startup_migrations(conn: AsyncConnection) -> None:
    """Apply safe schema upgrades for existing MySQL databases."""
    dialect = conn.dialect.name
    if dialect != "mysql":
        return

    has_user_id = await conn.execute(
        text(
            """
            SELECT COUNT(*) FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'conversations'
              AND COLUMN_NAME = 'user_id'
            """
        )
    )
    if has_user_id.scalar() == 0:
        await conn.execute(text("ALTER TABLE conversations ADD COLUMN user_id CHAR(36) NULL"))

    has_user_id_index = await conn.execute(
        text(
            """
            SELECT COUNT(*) FROM information_schema.STATISTICS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'conversations'
              AND INDEX_NAME = 'idx_conversations_user_id'
            """
        )
    )
    if has_user_id_index.scalar() == 0:
        try:
            await conn.execute(
                text("CREATE INDEX idx_conversations_user_id ON conversations (user_id)")
            )
        except Exception:
            pass
