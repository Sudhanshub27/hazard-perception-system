# ============================================================
# Makefile — Common developer commands
#
# Usage: make <target>
# On Windows, install 'make' via: choco install make
#   OR just read these as documentation and run the commands
#   manually in your terminal.
# ============================================================

.PHONY: help setup setup-model setup-api dev-model dev-api \
        docker-build docker-up docker-down docker-logs clean

# Default target — show help
help:
	@echo ""
	@echo "  Autonomous Hazard Perception System"
	@echo "  ====================================="
	@echo ""
	@echo "  Setup:"
	@echo "    make setup        - Create all Python virtual environments"
	@echo "    make setup-model  - Set up model service venv only"
	@echo "    make setup-api    - Set up API service venv only"
	@echo ""
	@echo "  Local Development:"
	@echo "    make dev-model    - Run model service locally (port 8001)"
	@echo "    make dev-api      - Run API service locally (port 8000)"
	@echo ""
	@echo "  Docker:"
	@echo "    make docker-build - Build all Docker images"
	@echo "    make docker-up    - Start all services (detached)"
	@echo "    make docker-down  - Stop all services"
	@echo "    make docker-logs  - Tail logs from all services"
	@echo ""
	@echo "  Cleanup:"
	@echo "    make clean        - Remove __pycache__ and .pyc files"
	@echo ""

# ============================================================
# Setup
# ============================================================
setup: setup-model setup-api
	@echo "All environments ready."

setup-model:
	@echo "Setting up model service..."
	cd model && python -m venv venv
	model\venv\Scripts\pip install -r model\requirements.txt
	@echo "Model service ready."

setup-api:
	@echo "Setting up API service..."
	cd api && python -m venv venv
	api\venv\Scripts\pip install -r api\requirements.txt
	@echo "API service ready."

# ============================================================
# Local Dev Servers
# ============================================================
dev-model:
	model\venv\Scripts\uvicorn src.main:app --reload --port 8001 --app-dir model

dev-api:
	api\venv\Scripts\uvicorn src.main:app --reload --port 8000 --app-dir api

dev-frontend:
	cd frontend && npm run dev

# ============================================================
# Docker
# ============================================================
docker-build:
	docker compose build

docker-up:
	docker compose up -d
	@echo "Services running:"
	@echo "  Frontend: http://localhost:3000"
	@echo "  API:      http://localhost:8000"
	@echo "  Model:    http://localhost:8001"

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

# ============================================================
# Cleanup
# ============================================================
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	@echo "Cleaned."
