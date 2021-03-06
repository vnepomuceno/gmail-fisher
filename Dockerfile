FROM python:3.9-slim

# Set up and activate virtual environment
ENV VIRTUAL_ENV "/venv"
RUN python -m venv $VIRTUAL_ENV
ENV PATH "$VIRTUAL_ENV/bin:$PATH"

WORKDIR ${VIRTUAL_ENV}
COPY ./pyproject.toml ${VIRTUAL_ENV}/
COPY ./poetry.lock ${VIRTUAL_ENV}/

# Python commands run inside the virtual environment
RUN python -m pip install --upgrade pip \
        parse \
        realpython-reader \
        poetry
RUN poetry install

COPY . ${VIRTUAL_ENV}/