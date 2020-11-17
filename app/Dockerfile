FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-slim

COPY requirements.txt /app/

RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt

COPY main.py /app/