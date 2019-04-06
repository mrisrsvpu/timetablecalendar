FROM ubuntu:18.04

ENV PORT 5000

EXPOSE 5000

WORKDIR /app

COPY . /app


RUN apt-get update && apt-get install -y python3-venv && mkdir -p /app && cd /app && python3 -m venv env && /app/env/bin/python -m pip install --upgrade pip && /app/env/bin/python -m pip install -r /app/requirements.txt

CMD ["/app/env/bin/python", "/app/app.py"]