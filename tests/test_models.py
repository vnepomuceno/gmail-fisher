from gmail_fisher.models import sort_as_dict


def test_sort_as_dict(food_expenses_5):
    sorted_list_dict = sort_as_dict(food_expenses_5)

    assert sorted_list_dict == [
        {
            "id": "86c78067-0dcc-4d67-952c-64b23dcff471",
            "service": "Uber Eats",
            "restaurant": "McDonalds",
            "total_euros": 8.8,
            "date": "2021-11-21",
        },
        {
            "id": "3c35ec0c-993d-4901-af98-653f8f9f74e3",
            "service": "Bolt Food",
            "restaurant": "DOTE",
            "total_euros": 12.5,
            "date": "2021-11-19",
        },
        {
            "id": "d4f6dcad-90ef-44d1-9e99-621b83f779c5",
            "service": "Bolt Food",
            "restaurant": "Sushicome",
            "total_euros": 22.3,
            "date": "2021-11-14",
        },
        {
            "id": "8eb5831f-e4bd-46b9-9180-b66fb298beea",
            "service": "Uber Eats",
            "restaurant": "Pizza Hut",
            "total_euros": 12.5,
            "date": "2021-11-13",
        },
        {
            "id": "79aa8544-aa05-4a0c-8120-a83b665dbed2",
            "service": "Bolt Food",
            "restaurant": "Portugália",
            "total_euros": 18.5,
            "date": "2021-11-11",
        },
    ]
