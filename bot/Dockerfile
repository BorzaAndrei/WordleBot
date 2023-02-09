FROM python:3.9.15

ENV BIND_PORT 5000
ENV REDIS_HOST localhost
ENV REDIS_PORT 6379
ENV BOT_TOKEN token

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .

EXPOSE $BIND_PORT

CMD ["python3", "main.py"]
