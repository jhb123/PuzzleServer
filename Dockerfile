FROM python:3.11-slim

COPY . /app
WORKDIR /app
RUN pip3 install ".[local]"
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run_server:app"]
