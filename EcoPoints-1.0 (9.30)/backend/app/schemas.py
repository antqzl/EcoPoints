"""Pydantic request and response schemas. / Pydantic 请求和响应结构。"""
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)

class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    campus: str | None = Field(default=None, max_length=120)
    department: str | None = Field(default=None, max_length=120)

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    full_name: str
    email: EmailStr
    role: str
    campus: str | None = None
    department: str | None = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

class InitiativeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str
    category: str
    points: int
    start_date: datetime | None = None
    end_date: datetime | None = None

class RewardOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str
    points_cost: int
    stock: int

class HomeSummary(BaseModel):
    balance: int
    activities_this_week: int
    rewards_redeemed: int
    energy_rank: int | None
    initiatives: list[InitiativeOut]
    energy_usage_kwh: Decimal
    energy_change_percent: float | None

class DashboardSummary(BaseModel):
    period: str
    campus: str | None
    area: str | None
    points_earned: int
    activities: int
    energy_usage_kwh: Decimal
    participation_rate: float
    energy_trend: list[dict]
    participation_by_category: list[dict]
    energy_leaderboard: list[dict]
    user_leaderboard: list[dict]
