.PHONY: help install test lint format clean run-example run-api perf-test security-test setup starter

help:
	@echo "🚀 NovaSandbox - Development commands"
	@echo ""
	@echo "SETUP:"
	@echo "  setup         - Automatická instalace (./setup.sh)"
	@echo "  install       - Install Python dependencies"
	@echo ""
	@echo "TESTOVÁNÍ:"
	@echo "  test          - Run unit tests"
	@echo "  perf-test     - Run performance benchmark (4600 operací)"
	@echo "  security-test - Run security vulnerability tests"
	@echo "  test-bench    - Run benchmark tests"
	@echo ""
	@echo "SPUŠTĚNÍ:"
	@echo "  starter       - Run starter kit (5 praktických příkladů)"
	@echo "  run-example   - Run basic example"
	@echo "  run-api       - Run REST API server (http://localhost:8000)"
	@echo ""
	@echo "VÝVOJ:"
	@echo "  lint          - Run linters (flake8, mypy)"
	@echo "  format        - Format code with black and isort"
	@echo "  coverage      - Run tests with coverage report"
	@echo "  clean         - Remove build artifacts and cache files"

install:
	pip install -r requirements.txt

install-dev:
	pip install -e .[dev]
	pip install -e .[api]

test:
	pytest tests/test_sandbox.py -v

test-bench:
	pytest tests/benchmark.py -v --benchmark-only

coverage:
	pytest tests/ --cov=core --cov=providers --cov-report=html --cov-report=term

lint:
	flake8 core/ providers/ tests/ examples/ --max-line-length=100
	mypy core/ providers/ --ignore-missing-imports

format:
	black core/ providers/ tests/ examples/ --line-length=100
	isort core/ providers/ tests/ examples/ --profile=black

clean:
	rm -rf build/ dist/ *.egg-info/
	rm -rf .pytest_cache/ .mypy_cache/ .coverage htmlcov/
	rm -rf __pycache__ core/__pycache__ providers/__pycache__ tests/__pycache__
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

setup:
	chmod +x setup.sh
	./setup.sh

starter:
	python3 examples/starter_kit.py

run-example:
	python3 examples/basic_usage.py

run-api:
	python3 examples/api_server.py

perf-test:
	python3 examples/performance_test.py

security-test:
	python3 examples/security_test.py

install:
	pip install -r requirements.txt

install-dev:
	pip install -e .[dev]

test:
	pytest tests/test_sandbox.py -v

test-bench:
	pytest tests/benchmark.py -v

coverage:
	pytest tests/ --cov=core --cov=providers --cov-report=html

lint:
	flake8 core/ providers/ tests/ examples/ --max-line-length=100

format:
	black core/ providers/ tests/ examples/ --line-length=100

docs:
	@echo "Documentation available in README.md"
	@echo "Generate API docs with: python -m pydoc -w core.hypervisor"

.PHONY: all
all: clean install test lint
