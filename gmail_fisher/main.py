from fastapi import FastAPI

from gmail_fisher.services.food import get_food_expenses


app = FastAPI()


@app.get("/expenses/food")
def read_food_expenses():
    return get_food_expenses()
