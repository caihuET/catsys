FROM python:3.9-slim
WORKDIR /app
COPY api-gateway/requirements.txt ./api-gateway/
RUN pip install --no-cache-dir -r api-gateway/requirements.txt
COPY api-gateway/ ./api-gateway/
COPY src/ ./src/
EXPOSE 9002
CMD ["python", "api-gateway/app.py"]
