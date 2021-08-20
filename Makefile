dev-configure:
	pip3 install -r quantlib/requirements.txt
	pip3 install -r requirements-dev.txt
	pre-commit install

build:
	docker build -t monte-carlo-simulator:latest -f ./quantlib/Dockerfile quantlib

install-redis:
	helm repo add bitnami https://charts.bitnami.com/bitnami
	helm install redis-trading bitnami/redis -n trading --set auth.password=password

uninstall-redis:
	helm uninstall redis-trading -n trading


