"""EcoPoints FastAPI app for local course demonstration.
用于课程演示的 EcoPoints FastAPI 应用。
"""
from datetime import datetime, timedelta
from decimal import Decimal
from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .config import get_settings
from .database import Base, engine, get_db
from .dependencies import get_current_user
from .models import EnergyReading, Initiative, PointTransaction, Redemption, Reward, User
from .schemas import DashboardSummary, HomeSummary, InitiativeOut, LoginRequest, RegisterRequest, RewardOut, TokenResponse, UserOut
from .security import create_access_token, hash_password, verify_password

settings = get_settings()
app = FastAPI(title="EcoPoints API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

@app.on_event("startup")
def create_tables() -> None:
    # Convenient for a local demo; production would use migrations.
    # 方便本地演示；生产项目应使用迁移工具。
    Base.metadata.create_all(bind=engine)

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "ecopoints-api"}

@app.post("/api/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email or password is incorrect")
    return TokenResponse(access_token=create_access_token(user.id), user=UserOut.model_validate(user))

@app.post("/api/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> TokenResponse:
    # Create a local demo account; email verification is outside this classroom project.
    # 创建本地演示账号；邮箱验证不属于本课程项目范围。
    email = payload.email.lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This email is already registered")
    user = User(
        full_name=payload.full_name.strip(), email=email, password_hash=hash_password(payload.password),
        campus=payload.campus, department=payload.department, role="student",
    )
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This email is already registered")
    return TokenResponse(access_token=create_access_token(user.id), user=UserOut.model_validate(user))

@app.get("/api/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user

@app.get("/api/initiatives", response_model=list[InitiativeOut])
def list_initiatives(db: Session = Depends(get_db)) -> list[Initiative]:
    return list(db.scalars(select(Initiative).where(Initiative.is_active.is_(True)).order_by(Initiative.start_date)).all())

@app.get("/api/rewards", response_model=list[RewardOut])
def list_rewards(db: Session = Depends(get_db)) -> list[Reward]:
    return list(db.scalars(select(Reward).where(Reward.is_active.is_(True)).order_by(Reward.points_cost)).all())

@app.post("/api/rewards/{reward_id}/redeem")
def redeem_reward(reward_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    # Redeem one reward atomically enough for this local classroom demo.
    # 本地课堂演示中，兑换流程在一次数据库事务中完成。
    reward = db.get(Reward, reward_id)
    if not reward or not reward.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reward not found")
    if reward.stock <= 0:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This reward is out of stock")
    balance = int(db.scalar(select(func.coalesce(func.sum(PointTransaction.points), 0)).where(PointTransaction.user_id == current_user.id)) or 0)
    spent = int(db.scalar(select(func.coalesce(func.sum(Redemption.points_spent), 0)).where(Redemption.user_id == current_user.id)) or 0)
    available = balance - spent
    if available < reward.points_cost:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You do not have enough EcoPoints")
    db.add(Redemption(user_id=current_user.id, reward_id=reward.id, points_spent=reward.points_cost, status="requested"))
    reward.stock -= 1
    db.commit()
    return {"message": "Reward redeemed successfully", "reward": reward.name, "remaining_points": available - reward.points_cost, "stock": reward.stock}

@app.get("/api/home/summary", response_model=HomeSummary)
def home_summary(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> HomeSummary:
    balance = db.scalar(select(func.coalesce(func.sum(PointTransaction.points), 0)).where(PointTransaction.user_id == current_user.id)) or 0
    week_start = datetime.utcnow() - timedelta(days=7)
    activities = db.scalar(select(func.count(PointTransaction.id)).where(PointTransaction.user_id == current_user.id, PointTransaction.created_at >= week_start)) or 0
    redeemed = db.scalar(select(func.count(Redemption.id)).where(Redemption.user_id == current_user.id)) or 0
    initiatives = list(db.scalars(select(Initiative).where(Initiative.is_active.is_(True)).order_by(Initiative.start_date).limit(3)).all())
    latest_energy = db.scalar(select(EnergyReading.usage_kwh).order_by(EnergyReading.period_start.desc())) or Decimal("0")
    return HomeSummary(balance=int(balance), activities_this_week=int(activities), rewards_redeemed=int(redeemed), energy_rank=None, initiatives=initiatives, energy_usage_kwh=latest_energy, energy_change_percent=None)

@app.get("/api/dashboard/summary", response_model=DashboardSummary)
def dashboard_summary(
    period: str = Query("This Month"), campus: str | None = Query(None), area: str | None = Query(None),
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db),
) -> DashboardSummary:
    # Query parameters keep classroom filtering easy to understand.
    # 查询参数让课堂演示中的筛选逻辑更容易理解。
    energy_query = select(EnergyReading)
    if campus:
        energy_query = energy_query.where(EnergyReading.campus == campus)
    if area:
        energy_query = energy_query.where(EnergyReading.area == area)
    readings = list(db.scalars(energy_query.order_by(EnergyReading.period_start)).all())
    points = int(db.scalar(select(func.coalesce(func.sum(PointTransaction.points), 0))) or 0)
    activities = int(db.scalar(select(func.count(PointTransaction.id))) or 0)
    total_energy = sum((reading.usage_kwh for reading in readings), Decimal("0"))
    participation = sum(reading.participation_count for reading in readings)
    energy_rows = db.execute(
        select(EnergyReading.building, func.sum(EnergyReading.usage_kwh).label("usage_kwh"))
        .group_by(EnergyReading.building)
        .order_by(func.sum(EnergyReading.usage_kwh))
        .limit(5)
    ).all()
    user_rows = db.execute(
        select(User.full_name, User.department, func.sum(PointTransaction.points).label("points"))
        .join(PointTransaction, PointTransaction.user_id == User.id)
        .group_by(User.id, User.full_name, User.department)
        .order_by(func.sum(PointTransaction.points).desc())
        .limit(5)
    ).all()
    category_rows = db.execute(
        select(Initiative.category, func.count(PointTransaction.id).label("activities"))
        .join(PointTransaction, PointTransaction.initiative_id == Initiative.id)
        .group_by(Initiative.category)
    ).all()
    return DashboardSummary(
        period=period, campus=campus, area=area, points_earned=points, activities=activities,
        energy_usage_kwh=total_energy, participation_rate=float(participation),
        energy_trend=[{"period_start": r.period_start.isoformat(), "usage_kwh": float(r.usage_kwh)} for r in readings],
        participation_by_category=[{"category": row.category, "activities": int(row.activities)} for row in category_rows],
        energy_leaderboard=[{"building": row.building, "usage_kwh": float(row.usage_kwh)} for row in energy_rows],
        user_leaderboard=[{"name": row.full_name, "department": row.department, "points": int(row.points)} for row in user_rows],
    )
