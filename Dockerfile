FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY config ./config
COPY examples ./examples
RUN pip install --no-cache-dir -e .

CMD ["python", "-m", "quantlab.main", "--help"]
