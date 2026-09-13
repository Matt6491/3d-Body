FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt
COPY backend /app/backend
COPY body-model /app/body-model
COPY computer-vision /app/computer-vision
COPY adaptation-engine /app/adaptation-engine
COPY exercise-data /app/exercise-data
EXPOSE 8000
CMD ["uvicorn","backend.app.main:app","--host","0.0.0.0","--port","8000"]
