FROM python:3.7-slim

ENV PYTHONDONTWRITEBYTECODE=1

COPY requirements.txt ./

RUN pip3 install -r requirements.txt

COPY . .

CMD ["python3", "-u", "task_sender.py"]