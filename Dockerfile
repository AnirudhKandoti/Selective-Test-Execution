
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONPATH=/app

CMD ["bash", "-lc", "python -m src.cli.ste_cli record-run --project ${PROJECT_PATH:-examples/payments} && python -m src.cli.ste_cli select --project ${PROJECT_PATH:-examples/payments} && python -m src.cli.ste_cli run-selected --project ${PROJECT_PATH:-examples/payments}"]
