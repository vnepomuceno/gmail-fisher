import pytest

from gmail_fisher.data.models import UberEatsExpense, BoltFoodExpense
from gmail_fisher.parsers.food import FoodExpenseParser, BoltFoodParser, UberEatsParser


@pytest.mark.parametrize(
    "input_value, expected_output",
    [
        ("Sushi Place (General Roçadas)", "Sushi Place"),
        ("Honorato - Saldanha Av. Miguel Bombarda, 23B", "Honorato"),
        ("Pizza Lizzy", "Pizza Lizzy"),
        (
            "Sabores do Campo Centro de Lazer do Campo Pequeno loja 412",
            "Sabores do Campo",
        ),
        ("Chimarrão Praça do Chile 8 Lisboa 1000", "Chimarrão"),
        ("Chickinho Rua Marquês de Fronteira 117F", "Chickinho"),
        ("Hello Beijing Av. Da República, 97 B", "Hello Beijing"),
        ("Udon Av. Duque de Ávila 46B", "Udon"),
    ],
)
def test_apply_restaurant_filters(input_value, expected_output):
    result = FoodExpenseParser.apply_restaurant_filters(input_value)

    assert result == expected_output


def test_parse_bolt_expenses_from_messages(bolt_food_messages):
    parsed_expenses = BoltFoodParser().parse_expenses_from_messages(bolt_food_messages)
    assert parsed_expenses == [
        BoltFoodExpense(
            id="179f7511b28528cd",
            restaurant="Chickinho",
            total=9.73,
            date="2021-06-10",
        ),
        BoltFoodExpense(
            id="17914b9e89b41e02",
            restaurant="Sushicome",
            total=15.8,
            date="2021-04-27",
        ),
    ]


def test_parse_uber_eats_expenses_from_messages(uber_eats_messages):
    parsed_expenses = UberEatsParser().parse_expenses_from_messages(uber_eats_messages)
    assert parsed_expenses == [
        UberEatsExpense(
            id="17570b788e2319d0",
            restaurant="Pizza Lizzy",
            total=16.95,
            date="2020-10-28",
        ),
        UberEatsExpense(
            id="174a7fef0d8cdef3",
            restaurant="Poke House",
            total=10.9,
            date="2020-09-19",
        ),
    ]
