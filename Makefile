format:
	isort project/*
	black project/*

lint:
	isort --check-only project/*
	black --check project/*
	flake8 project/*

test:
	PYTHONPATH=./project pytest