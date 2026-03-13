PYTHON ?= python3
PIP ?= pip3

.PHONY: help install init-env run-embedding run-llm run-retrieval up down logs ps health check test

help:
	@echo "Available commands:"
	@echo "  make install        # Install Python dependencies"
	@echo "  make init-env       # Create .env from .env.example if missing"
	@echo "  make run-embedding  # Run Embedding Service locally (port 8001)"
	@echo "  make run-llm        # Run LLM Generation Service locally (port 8002)"
	@echo "  make run-retrieval  # Run Retrieval Service locally (port 8000)"
	@echo "  make up             # Start all services with docker compose"
	@echo "  make down           # Stop docker compose services"
	@echo "  make logs           # Tail docker compose logs"
	@echo "  make ps             # Show docker compose service status"
	@echo "  make health         # Check health endpoints"
	@echo "  make check          # Run basic syntax checks"
	@echo "  make test           # Run pytest test suite"

install:
	$(PIP) install -r requirements.txt

init-env:
	@if [ ! -f .env ]; then cp .env.example .env && echo ".env created from .env.example"; else echo ".env already exists"; fi

run-embedding:
	uvicorn embedding.app.main:app --host 0.0.0.0 --port 8001

run-llm:
	uvicorn llm_generation.app.main:app --host 0.0.0.0 --port 8002

run-retrieval:
	uvicorn retrieval.app.main:app --host 0.0.0.0 --port 8000

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f --tail=100

ps:
	docker compose ps

health:
	curl -s http://localhost:8001/healthz | cat
	curl -s http://localhost:8002/healthz | cat
	curl -s http://localhost:8000/healthz | cat

check:
	$(PYTHON) -m compileall embedding retrieval llm_generation

test:
	$(PYTHON) -m pytest -q
