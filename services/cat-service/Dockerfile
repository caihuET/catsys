FROM python:3.9-slim
WORKDIR /app
COPY services/cat-service/requirements.txt ./services/cat-service/
RUN pip install --no-cache-dir -r services/cat-service/requirements.txt
COPY services/cat-service/ ./services/cat-service/
COPY src/ ./src/
EXPOSE 5003
CMD ["uvicorn", "services.cat-service.app.main:app", "--host", "0.0.0.0", "--port", "5003"]
