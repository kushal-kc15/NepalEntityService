FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml poetry.lock README.md ./
COPY nes/ ./nes/
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --extras api --only=main

COPY . .

EXPOSE 8000

CMD ["nes-api"]