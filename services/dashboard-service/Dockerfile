FROM python:3.9-slim
WORKDIR /app
COPY services/dashboard-service/requirements.txt ./services/dashboard-service/
RUN pip install --no-cache-dir -r services/dashboard-service/requirements.txt
COPY services/dashboard-service/ ./services/dashboard-service/
COPY src/ ./src/
EXPOSE 5006
CMD ["uvicorn", "services.dashboard-service.app.main:app", "--host", "0.0.0.0", "--port", "5006"]
