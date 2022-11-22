# Global ARG, available to all stages (if renewed)
ARG WORKDIR="/app"

FROM python:3.10 AS builder

# Renew (https://stackoverflow.com/a/53682110):
ARG WORKDIR

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN pip install poetry && poetry config virtualenvs.in-project true

WORKDIR ${WORKDIR}
COPY . .
COPY docker/entrypoints/api.sh ./run.sh

RUN poetry install --only main

FROM python:3.10-slim

ARG WORKDIR

WORKDIR ${WORKDIR}

COPY --from=builder ${WORKDIR} .

# # For options, see https://boxmatrix.info/wiki/Property:adduser
# RUN adduser app -DHh ${WORKDIR} -u 1000
# USER 1000
