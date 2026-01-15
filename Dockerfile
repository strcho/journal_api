FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY Pipfile Pipfile.lock ./
RUN pip install pipenv && \
    pipenv install --system --deploy --ignore-pipfile

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main_v2:app", "--host", "0.0.0.0", "--port", "8000"]
