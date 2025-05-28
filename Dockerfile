FROM python:3.11-slim AS base

WORKDIR /

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app
COPY run.py ./run.py
CMD ["python", "run.py"]

EXPOSE 8080
