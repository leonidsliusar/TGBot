import os
from typing import List
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy import create_engine, text, Integer, String, ForeignKey
from dotenv import load_dotenv
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# Config
load_dotenv()
login = os.getenv('DB_LOGIN')
password = os.getenv('DB_PASS')
host = os.getenv('DB_HOST')
db_name = os.getenv('DB_NAME')
db_type = os.getenv('DB')

engine = create_engine(f'{db_type}://{login}:{password}@{host}/{db_name}', echo=True)
if not database_exists(engine.url):
    create_database(engine.url)


Base = declarative_base()


class Chat(Base):
    __tablename__ = 'chats'

    chat_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    messages: Mapped[List["Messages"]] = relationship(back_populates='chat', cascade="all, delete-orphan")

    def __repr__(self):
        return f'{self.chat_id}, {self.messages}'

class Messages(Base):
    __tablename__ = 'messages'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey('chats.chat_id', ondelete='CASCADE'))
    chat: Mapped["Chat"] = relationship("Chat", back_populates='messages')
    message: Mapped[str] = mapped_column(String)

    def __repr__(self):
        return f'{self.id}, {self.message}'

if __name__ == '__main__':
    Base.metadata.create_all(engine)


# with engine.connect() as connection:
#    result = connection.execute(text('CREATE TABLE chats'))
#    print(result.all())
