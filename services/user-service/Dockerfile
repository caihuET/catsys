FROM python:3.9-slim
WORKDIR /app
COPY services/user-service/requirements.txt ./services/user-service/
RUN pip install --no-cache-dir -r services/user-service/requirements.txt
COPY services/user-service/ ./services/user-service/
COPY src/ ./src/
EXPOSE 5001
CMD ["uvicorn", "services.user-service.app.main:app", "--host", "0.0.0.0", "--port", "5001"]
