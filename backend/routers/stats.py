"""项目统计路由 —— GET /stats 返回统计信息"""

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models import Project as ProjectModel

router = APIRouter(prefix="/stats", tags=["统计"])


@router.get("")
async def get_stats(db: AsyncSession = Depends(get_db)):
    """返回项目统计信息"""
    # ① 项目总数（提示：db.scalar(select(func.count(...)))）
    total = await db.scalar(select(func.count(ProjectModel.id)))

    # ② 已完成的（status == "completed" 的个数）
    completed = await db.scalar(select(func.count(ProjectModel.id)).where(ProjectModel.status == "completed"))

    # ③ 待处理的
    pending = await db.scalar(select(func.count(ProjectModel.id)).where(ProjectModel.status == "pending"))

    # ④ 计算完成率（保留 1 位小数）
    success_rate = round(completed / total * 100, 1) if total > 0 else 0.0

    return {
        "total_projects": total,
        "completed": completed,
        "pending": pending,
        "success_rate": success_rate,
    }