import os
from typing import List
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy import create_engine, Integer, String, ForeignKey
from dotenv import load_dotenv
from sqlalchemy.orm import Mapped, mapped_column, relationship


# Config
load_dotenv()
login = os.getenv('DB_LOGIN')
password = os.getenv('DB_PASS')
host = os.getenv('DB_HOST')
db_name = os.getenv('DB_NAME')


engine = create_engine(f'postgresql://{login}:{password}@{host}/{db_name}', echo=True)
Base = declarative_base()


class Chat(Base):
    __tablename__ = 'chats'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    messages: Mapped[List["Messages"]] = relationship(back_populates='chat', cascade="all, delete-orphan")

    def __repr__(self):
        return f'{self.chat_id}, {self.messages}'

class Messages(Base):
    __tablename__ = 'messages'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey('chats.id', ondelete='CASCADE'))
    chat: Mapped["Chat"] = relationship("Chat", back_populates='messages')
    message: Mapped[str] = mapped_column(String)

    def __repr__(self):
        return f'{self.id}, {self.message}'

if __name__ == '__main__':
    Base.metadata.create_all(engine)


session = Session(engine)