FROM python:3.8

COPY . .

RUN apt update && apt install -y \
    nmap iputils-ping

RUN pip3 install -r requirements

CMD ["python3", "frontend.py"]
