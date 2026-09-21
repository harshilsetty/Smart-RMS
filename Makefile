# Smart RMS - Automation Makefile

.PHONY: help install seed dev-backend dev-frontend test lint clean

help:
	@echo "Smart RMS - Commands:"
	@echo "  make install      Install backend and frontend dependencies"
	@echo "  make seed         Seed and validate mock RMS data"
	@echo "  make dev-backend  Run FastAPI backend locally on port 8000"
	@echo "  make dev-frontend Run Vite frontend locally on port 5173"
	@echo "  make test         Run backend unit & integration tests"
	@echo "  make health       Check health of local API"
	@echo "  make clean        Remove cache and build artifacts"

install:
	pip install -r backend/requirements.txt
	cd frontend && npm install

seed:
	python scripts/seed_mock_data.py

dev-backend:
	cd backend && uvicorn app.main:app --reload --port 8000

dev-frontend:
	cd frontend && npm run dev

test:
	cd backend && pytest tests/ -v

health:
	python scripts/health_check.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf backend/.pytest_cache frontend/dist
