install:
	pip install -e ".[dev]"
init-db:
	python scripts/create_tables.py
run:
	uvicorn app.main:app --reload
test:
	pytest
lint:
	ruff check .
