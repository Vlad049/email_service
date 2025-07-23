from typing import Optional, List, Annotated
import asyncio

from fastapi import FastAPI, HTTPException, status, BackgroundTasks, Depends, Query, Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import uvicorn

from models import get_db, User, Message
from pydantic_models import UserModel, MessageModel, MessageResponse, UserModelResponse


app = FastAPI()


async def send_mail(message_model: MessageModel, db: Annotated[AsyncSession, Depends(get_db)]):
    user: Optional[User] = await db.scalar(select(User).filter_by(login=message_model.login))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Для відправки повідомлень зареєструйтесь"
            )
    
    message = Message(send_mail=message_model.send_mail, user=user)
    db.add(message)
    await db.commit()
    await db.refresh(message)

    await asyncio.sleep(5)
    message.answer_mail = f"Отримана відповідь для користувача {message_model.login}. Привіт отримав твоє повідомлення."
    await db.commit()


@app.post("/users/", status_code=status.HTTP_201_CREATED, response_model=UserModelResponse)
async def create_user(user_model: UserModel, db: Annotated[AsyncSession, Depends(get_db)]):
    user = User(**user_model.model_dump())
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@app.post("/message/", status_code=status.HTTP_202_ACCEPTED)
async def send_mail_route(
    message_model: MessageModel,
    db: Annotated[AsyncSession, Depends(get_db)],
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(send_mail, message_model, db)
    return dict(message="Повідомлення поставлено в чергу на відправку")


@app.get("/message/", status_code=status.HTTP_202_ACCEPTED, response_model=List[MessageResponse])
async def get_messages(db: Annotated[AsyncSession, Depends(get_db)], login: str = Query(...)):
    user: Optional[User] = await db.scalar(select(User).filter_by(login=login))
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    return user.messages


@app.get("/messages/{message_id}/", status_code=status.HTTP_202_ACCEPTED, response_model=MessageResponse)
async def get_message(
    db: Annotated[AsyncSession, Depends(get_db)],
    login: str = Query(...),
    message_id: int = Path(...)
):
    user: Optional[User] = await db.scalar(select(User).filter_by(login=login))
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    return await db.scalar(select(Message).filter_by(user=user, id=message_id))


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)