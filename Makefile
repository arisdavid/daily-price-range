dev-configure:
	pip3 install -r quantlib/requirements.txt
	pip3 install -r tasksender/requirements.txt
	pip3 install -r taskworker/requirements.txt
	pip3 install -r requirements-dev.txt
	pre-commit install

build:
	docker build -t monte-carlo-simulator:latest -f ./quantlib/Dockerfile quantlib
	docker build -t task-sender:latest -f ./tasksender/Dockerfile tasksender
	docker build -t task-worker:latest -f ./taskworker/Dockerfile taskworker

install:
	kubectl create -f minikube-rbac.yaml -n trading
	helm repo add bitnami https://charts.bitnami.com/bitnami
	helm install redis-trading bitnami/redis -n trading --set auth.password=password
	helm install rabbitmq-trading bitnami/rabbitmq -n trading --set auth.username=admin,auth.password=admin
	kubectl create secret generic rmq-creds --from-env-file=.env -n trading
	sleep 60 #create an initContainers to wait for other pods to be available before deploying minikube-deployment.yaml
	kubectl create -f minikube-deployment.yaml -n trading

uninstall:
	kubectl delete -f minikube-rbac.yaml -n trading
	kubectl delete sa taskmanager-sa -n trading
	helm uninstall redis-trading -n trading
	kubectl delete secret rmq-creds -n trading
	helm uninstall rabbitmq-trading -n trading
	kubectl delete -f minikube-deployment.yaml -n trading

sendtask:
	kubectl exec tasksender-5d599d66f5-sh6mp -n trading -- sh -c "python3 -u task_sender.py -l AAPL AMZN CRWD UPST"