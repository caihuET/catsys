FROM python:3.9-slim
WORKDIR /app
COPY services/crm-service/requirements.txt ./services/crm-service/
RUN pip install --no-cache-dir -r services/crm-service/requirements.txt
COPY services/crm-service/ ./services/crm-service/
COPY src/ ./src/
EXPOSE 5004
CMD ["uvicorn", "services.crm-service.app.main:app", "--host", "0.0.0.0", "--port", "5004"]
