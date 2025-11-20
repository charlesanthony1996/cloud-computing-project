FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

# COPY anomaly-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt kaggle
# RUN pip install --no-cache-dir \
#     --extra-index-url https://download.pytorch.org/whl/cpu \
#     -r requirements.txt kaggle

COPY kaggle.json /root/.kaggle/kaggle.json
RUN chmod 600 /root/.kaggle/kaggle.json

# download and unzip the dataset
# RUN apt-get update && apt-get install -y unzip && \
#     kaggle datasets download -d charlesanthony1996/mjff-train-defog-folder -p /app && \
#     unzip /app/mjff-train-defog-folder.zip -d /app/train && \
#     rm /app/mjff-train-defog-folder.zip
#     echo "=== DEBUG CONTENT ===" && ls -R /app/train

# download and unzip the dataset
RUN rm -rf /app/train || true && \
    apt-get update && apt-get install -y unzip && \
    kaggle datasets download -d charlesanthony1996/mjff-train-defog-folder -p /app && \
    unzip /app/mjff-train-defog-folder.zip -d /app/train && \
    rm /app/mjff-train-defog-folder.zip
    # echo "=== DEBUG CONTENT ===" && ls -R /app/train


# RUN echo "=== DEBUG CONTENT ===" && ls -R /app/train

COPY . .

EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]