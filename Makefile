.PHONY: help install dev test docker-up docker-down docker-logs docker-build clean

help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make dev        - Start development server"
	@echo "  make test       - Run tests"
	@echo "  make docker-up   - Start Docker Compose services"
	@echo "  make docker-down - Stop Docker Compose services"
	@echo "  make docker-logs - View Docker Compose logs"
	@echo "  make docker-build - Build Docker image"
	@echo "  make clean      - Clean Python cache and build artifacts"

install:
	pipenv install --dev

dev:
	pipenv run uvicorn app.main_v2:app --reload --host 0.0.0.0 --port 8000

test:
	pipenv run pytest -v

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f api

docker-build:
	docker build -t journal-api .

docker-prod-up:
	docker-compose -f docker-compose.prod.yml up -d

docker-prod-down:
	docker-compose -f docker-compose.prod.yml down

clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	find . -type d -name '.pytest_cache' -delete
	rm -rf build dist
