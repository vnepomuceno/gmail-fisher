FROM python:3.11.0b3-bullseye

# Set up and activate virtual environment
ENV VIRTUAL_ENV "/venv"
RUN python -m venv $VIRTUAL_ENV
ENV PATH "$VIRTUAL_ENV/bin:$PATH"

WORKDIR ${VIRTUAL_ENV}
COPY ./pyproject.toml ${VIRTUAL_ENV}/
COPY ./poetry.lock ${VIRTUAL_ENV}/

# Python commands run inside the virtual environment
RUN python -m pip install --no-cache-dir --upgrade pip==22.1.2 \
        parse==1.19.0 \
        realpython-reader==1.1.1 \
        poetry==1.1.13 \
    && poetry install

COPY . ${VIRTUAL_ENV}/

CMD ["poetry", "run", "export_food_expenses", "--output-filepath='output/food_expenses.json'"]