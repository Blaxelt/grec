.PHONY: backend frontend dev

# Run the FastAPI backend (port 8000)
backend:
	fastapi dev backend/app/main.py

# Run the Vite frontend dev server (port 5173)
frontend:
	cd frontend && npm run dev

# Run both in parallel — stop everything with Ctrl+C
dev:
	$(MAKE) -j2 backend frontend
