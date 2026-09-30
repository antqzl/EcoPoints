"""Insert repeatable local demo data. / 写入可重复执行的本地演示数据。"""
from datetime import datetime
from pathlib import Path
import sys

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
from backend.app.database import Base, SessionLocal, engine
from backend.app.models import EnergyReading, Initiative, PointTransaction, Reward, User
from backend.app.security import hash_password

Base.metadata.create_all(bind=engine)
db = SessionLocal()
try:
    user = db.query(User).filter_by(email="sarah.tan@example.edu").first()
    if not user:
        user = User(full_name="Sarah Tan", email="sarah.tan@example.edu", password_hash=hash_password("EcoPointsDemo123!"), role="student", campus="Main Campus", department="Environmental Studies")
        db.add(user)
        db.flush()
    initiative_data = [
        ("Sustainable Transport Week", "Cycle, walk or take public transport to earn extra EcoPoints.", "transport", 50),
        ("Campus Green-Up", "Join tree planting and campus clean-up activities.", "volunteering", 100),
        ("Energy Saving Challenge", "Reduce energy usage and help your campus reach net zero.", "energy", 75),
    ]
    initiatives = []
    for title, description, category, points in initiative_data:
        item = db.query(Initiative).filter_by(title=title).first()
        if not item:
            item = Initiative(title=title, description=description, category=category, points=points, start_date=datetime(2024, 4, 1), is_active=True)
            db.add(item)
        initiatives.append(item)
    db.flush()
    if not db.query(PointTransaction).filter_by(user_id=user.id).first():
        for item, points in zip(initiatives, [500, 400, 350]):
            db.add(PointTransaction(user_id=user.id, initiative_id=item.id, points=points, note="Demo activity"))
    reward_data = [("Reusable Bottle", "A campus reusable bottle.", 300, 20), ("Coffee Voucher", "A small campus cafe voucher.", 500, 10)]
    for name, description, cost, stock in reward_data:
        if not db.query(Reward).filter_by(name=name).first():
            db.add(Reward(name=name, description=description, points_cost=cost, stock=stock, is_active=True))
    if not db.query(EnergyReading).first():
        for month, usage in enumerate([16500, 15800, 14900, 13800, 13000, 12540], start=1):
            db.add(EnergyReading(campus="Main Campus", area="Campus", building="All Buildings", period_start=datetime(2024, month, 1), usage_kwh=usage, participation_count=60 + month))
    db.commit()
    print("Demo data ready. Login: sarah.tan@example.edu / EcoPointsDemo123!")
finally:
    db.close()
