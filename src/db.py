from sqlalchemy import create_engine, Integer, String, BigInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from sqlalchemy.pool import StaticPool
from .config import settings

class Base(DeclarativeBase):
    pass

class TikTokUser(Base):
    __tablename__ = "tiktok_users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    open_id: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(256), default="")
    avatar_url: Mapped[str] = mapped_column(String(512), default="")
    access_token: Mapped[str] = mapped_column(String(2048), default="")
    refresh_token: Mapped[str] = mapped_column(String(2048), default="")
    token_expires_at: Mapped[int] = mapped_column(BigInteger, default=0)

def get_engine():
    url = settings.DATABASE_URL
    if url.startswith("sqlite:///"):
        # SQLite file
        return create_engine(url, connect_args={"check_same_thread": False})
    elif url.startswith("sqlite://"):
        # SQLite memory
        return create_engine(url, connect_args={"check_same_thread": False}, poolclass=StaticPool)
    else:
        return create_engine(url)

engine = get_engine()
Base.metadata.create_all(engine)

def get_session() -> Session:
    return Session(engine)
