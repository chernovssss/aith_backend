FROM python:3.11-slim

WORKDIR /hw_2

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y bash && rm -rf /var/lib/apt/lists/*
RUN python -m pip install --upgrade pip
RUN pip install poetry

COPY ../pyproject.toml .
COPY ../poetry.lock .
RUN POETRY_VIRTUALENVS_CREATE=false poetry install

COPY ../src src

CMD ["uvicorn", "src.main:app", "--port", "8080", "--host", "0.0.0.0"]