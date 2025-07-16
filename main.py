from typing import Optional, List, Annotated
import asyncio

from fastapi import FastAPI, HTTPException, status, BackgroundTasks, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import get_db, User, Message
from pydantic_models import UserModel, MessageModel, MessageResponse


app = FastAPI()


async def send_mail(message_model: MessageModel, db: Annotated[AsyncSession, Depends(get_db)]):
    user = Optional[User] = await db.scalar(select(User).filter_by(login=message_model.login))
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    message = Message(send_mail=message_model.send_mail, user=user)
    db.add(message)
    await db.commit()
    await db.refresh()

    await asyncio.sleep(5)
    message.answer_mail = f"Отримана відповідь для користувача {message_model.login}. Привіт отримав твоє повідомлення."
    await db.commit()