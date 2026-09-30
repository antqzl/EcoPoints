"""Database models. / 数据库模型。"""
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(40), default="student")
    campus: Mapped[str | None] = mapped_column(String(120))
    department: Mapped[str | None] = mapped_column(String(120))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    point_transactions: Mapped[list["PointTransaction"]] = relationship(back_populates="user")
    redemptions: Mapped[list["Redemption"]] = relationship(back_populates="user")

class Initiative(Base):
    __tablename__ = "initiatives"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    points: Mapped[int] = mapped_column(Integer, nullable=False)
    start_date: Mapped[datetime | None] = mapped_column(DateTime)
    end_date: Mapped[datetime | None] = mapped_column(DateTime)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    point_transactions: Mapped[list["PointTransaction"]] = relationship(back_populates="initiative")

class PointTransaction(Base):
    __tablename__ = "point_transactions"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    initiative_id: Mapped[int | None] = mapped_column(ForeignKey("initiatives.id"))
    points: Mapped[int] = mapped_column(Integer, nullable=False)
    note: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    user: Mapped[User] = relationship(back_populates="point_transactions")
    initiative: Mapped[Initiative | None] = relationship(back_populates="point_transactions")

class Reward(Base):
    __tablename__ = "rewards"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    points_cost: Mapped[int] = mapped_column(Integer, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    redemptions: Mapped[list["Redemption"]] = relationship(back_populates="reward")

class Redemption(Base):
    __tablename__ = "redemptions"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    reward_id: Mapped[int] = mapped_column(ForeignKey("rewards.id"), nullable=False)
    points_spent: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="requested")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    user: Mapped[User] = relationship(back_populates="redemptions")
    reward: Mapped[Reward] = relationship(back_populates="redemptions")

class EnergyReading(Base):
    __tablename__ = "energy_readings"
    id: Mapped[int] = mapped_column(primary_key=True)
    campus: Mapped[str] = mapped_column(String(120), nullable=False)
    area: Mapped[str] = mapped_column(String(120), nullable=False)
    building: Mapped[str] = mapped_column(String(160), nullable=False)
    period_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    usage_kwh: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    participation_count: Mapped[int] = mapped_column(Integer, default=0)
