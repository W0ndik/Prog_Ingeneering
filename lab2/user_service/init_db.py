from database import engine, SessionLocal
from models import Base, User
from passlib.hash import bcrypt

def init_db():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    if not db.query(User).filter_by(username="admin").first():
        admin_user = User(
            username="admin",
            password_hash=bcrypt.hash("secret")
        )
        db.add(admin_user)
        db.commit()

    db.close()
