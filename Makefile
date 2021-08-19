dev-configure:
	pip3 install -r quantlib/requirements.txt
	pip3 install -r requirements-dev.txt
	pre-commit install

build:
	docker build -t monte-carlo-simulator:latest -f ./quantlib/Dockerfile quantlib
