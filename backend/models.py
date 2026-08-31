"""数据库模型"""

from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """所有模型的基类"""

    pass


class Project(Base):
    """项目表 —— 对应 projects 表"""

    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(8), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    tech_stack: Mapped[list[str]] = mapped_column(JSON, default=lambda: ["python"])
    tags: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    generated_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # 一个项目有多条日志（一对多关系）
    logs: Mapped[list["AgentLog"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )


class AgentLog(Base):
    """Agent 执行日志表 —— 对应 agent_logs 表"""

    __tablename__ = "agent_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[str] = mapped_column(
        String(8), ForeignKey("projects.id", ondelete="CASCADE")
    )
    agent_name: Mapped[str] = mapped_column(String(50))
    action: Mapped[str] = mapped_column(String(20))  # 'think' | 'act'
    input_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    output_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # 日志属于哪个项目（多对一关系）
    project: Mapped["Project"] = relationship(back_populates="logs")
