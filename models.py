from typing import Optional, List
import asyncio

from sqlalchemy import String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship, declarative_base
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from config import settings

Base = declarative_base()
engine = create_async_engine(settings.sqlalchemy_uri, echo=True)
Session = async_sessionmaker(bind=engine, expire_on_commit=False)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    login: Mapped[str] = mapped_column(String(20), unique=True)
    messages: Mapped[List["Message"]] = relationship(back_populates="user", lazy="selectin")


class Message(Base):
    __tablename__ = "messages"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    send_mail: Mapped[str] = mapped_column(Text())
    answer_mail: Mapped[Optional[str]] = mapped_column(Text(), nullable=True, default=None)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="cascade", onupdate="cascade"))
    user: Mapped[User] = relationship(back_populates="messages", lazy="selectin")


async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    async with Session() as session:
        yield session


if __name__ == "__main__":
    asyncio.run(create_db())