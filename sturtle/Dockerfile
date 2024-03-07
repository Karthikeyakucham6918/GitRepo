# Replace '3.x' with your Python version
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt /app

RUN pip install -r requirements.txt

COPY .env /app

COPY sql_app.db /app

COPY . /app/sturtle

ENV PYTHONPATH "${PYTHONPATH}:/sturtle"

EXPOSE 8080

CMD uvicorn sturtle.main:app --host 0.0.0.0 --port 8080