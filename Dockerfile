FROM python:3.10.6-slim

RUN mkdir bot
WORKDIR bot

ADD requirements.txt /bot/requirements.txt
RUN pip install -r requirements.txt
ADD ../.. /bot/

CMD bash -c "alembic upgrade head && python ./main.py"
