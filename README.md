# Gmail Fisher

![Build Status](https://api.travis-ci.com/Vnepomuceno/gmail-fisher.svg?branch=master)

Automation scripts for interacting with Gmail API 🎣

## Run Scripts

### List Messages

Filters available messages with `KEYWORDS` and from `SENDER_EMAILS` and lists them.

Example:
```bash
poetry run list_messages --sender-email='portugal-food@bolt.eu' --keywords='Delivery'
```

### Save Attachments

Filters available messages with `KEYWORDS` and from `SENDER_EMAILS` and lists them.

If filtered messages contain attachments, then those will be downloaded
to an `output` directory and with a formatted name of `PaySlip_YYYY-MM.pdf`.

Example:
```bash
poetry run save_attachments --sender-email='me@my-company.com|payroll@my-company.com' --keywords='payslip'
```

### Plot Expenses

Filters available messages with `KEYWORDS` and from `SENDER_EMAILS` and lists them.

Tailored for UberEats receipts, it draws a bar plot with keys being the month and year in format `YYYY-MM` and
the values being the total of expenses payed for that month.

Example:
```bash
poetry run uber_eats_stats --sender-email='uber.portugal@uber.com' --keywords='Total'
```

### Export Food Expenses to JSON

Filters available messages with Uber Eats and Bolt Food expenses.

Scraps data from those messages to populate a `FoodExpense` iterable that will then be serialized to a Json file.

Example:
```bash
poetry run export_food_expenses --output-filepath='./gmail_fisher/output/food_expenses.json'
```

### Export Transportation Expenses to JSON

Filters available messages with Bolt expenses.

Scraps data from those messages to populate a `BoltTransportationExpense` iterable that will then be serialized to a Json file.

Example:
```bash
poetry run export_transport_expenses --output-filepath='./gmail_fisher/output/transport_expenses.json'
```