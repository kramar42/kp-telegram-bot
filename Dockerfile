FROM python:3-alpine

COPY . /bot
WORKDIR /bot

RUN pip install -r requirements.txt

ENV BOT_TOKEN=

CMD ["python3", "main.py"]
