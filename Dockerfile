FROM python:3.8.5-slim

# Set up and activate virtual environment
ENV VIRTUAL_ENV "/venv"
RUN python -m venv $VIRTUAL_ENV
ENV PATH "$VIRTUAL_ENV/bin:$PATH"

WORKDIR ${VIRTUAL_ENV}
COPY ./Pipfile* ${VIRTUAL_ENV}/

# Python commands run inside the virtual environment
RUN python -m pip install \
        parse \
        realpython-reader \
        pipenv
RUN pipenv install

COPY . ${VIRTUAL_ENV}/