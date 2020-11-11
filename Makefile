MAKE_FILE_PATH=$(abspath $(lastword $(MAKEFILE_LIST)))
CURRENT_DIR=$(dir $(MAKE_FILE_PATH))

format:
	isort project/*
	black project/*

lint:
	isort --check-only project/*
	black --check project/*
	flake8 project/*

tests:
	PYTHONPATH=./project pytest -n 4

build_docker:
	docker build -t mahjong_bot .

GAMES=1
run_battle:
	docker run -u `id -u` -it --rm \
		-v "$(CURRENT_DIR)project/:/app/" \
		mahjong_bot pypy3 bots_battle.py -g $(GAMES) $(ARGS)

run_on_tenhou:
	docker-compose up

archive_replays:
	tar -czvf "logs-$(shell date '+%Y-%m-%d-%H-%M').tar.gz" -C ./project/battle_results/logs/ .
	tar -czvf "replays-$(shell date '+%Y-%m-%d-%H-%M').tar.gz" -C ./project/battle_results/replays/ .