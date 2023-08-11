FROM python:3.11-slim-buster

COPY . /app
WORKDIR /app
RUN pip3 install .
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run_server:app"]
