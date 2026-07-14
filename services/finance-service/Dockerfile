FROM python:3.9-slim
WORKDIR /app
COPY services/finance-service/requirements.txt ./services/finance-service/
RUN pip install --no-cache-dir -r services/finance-service/requirements.txt
COPY services/finance-service/ ./services/finance-service/
COPY src/ ./src/
EXPOSE 5005
CMD ["uvicorn", "services.finance-service.app.main:app", "--host", "0.0.0.0", "--port", "5005"]
