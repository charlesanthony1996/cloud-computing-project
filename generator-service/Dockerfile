FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY main.py ./

ENV TARGET_URL=http://ingestion:8081/ingest

ENV SESSION_ID=s1

ENV RATE_HZ=10

CMD ["python", "main.py"]