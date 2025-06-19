from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.admin import Admin


async def get_all_admin_user_ids(db: AsyncSession):
    """
    Получить все user_id из таблицы admins.
    """
    result = await db.execute(select(Admin.user_id))
    return [row[0] for row in result.fetchall()]
