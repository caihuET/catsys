FROM python:3.9-slim
WORKDIR /app
COPY services/merchant-service/requirements.txt ./services/merchant-service/
RUN pip install --no-cache-dir -r services/merchant-service/requirements.txt
COPY services/merchant-service/ ./services/merchant-service/
COPY src/ ./src/
EXPOSE 5002
CMD ["uvicorn", "services.merchant-service.app.main:app", "--host", "0.0.0.0", "--port", "5002"]
