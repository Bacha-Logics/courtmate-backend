from app.db.base import Base
from app.db.session import engine

# Import all models here
from app.models.user import User
from app.models.case import Case
from app.models.hearing import Hearing

def init_db():
    Base.metadata.create_all(bind=engine)
