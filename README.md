# Gmail Fisher

![Build Status](https://api.travis-ci.com/Vnepomuceno/gmail-fisher.svg?branch=master)

Automation scripts for interacting with Gmail API 🎣

## Save Attachments

Filters available messages with `KEYWORDS` and from `SENDER_EMAILS` and lists them.

When the `--download-pdf` flag is inputted, if filtered messages contain attachments, then those will be downloaded
to an `output` directory and with a formatted name of `PaySlip_YYYY-MM.pdf`.

```
poetry run save_attachments --sender-email=<SENDER_EMAIL> --keywords=<KEYWORDS>
```

Example:
```bash
poetry run save_attachments --sender-email='me@my-company.com|payroll@my-company.com' --keywords='payslip' --download-pdf
```

## Plot Expenses

Filters available messages with `KEYWORDS` and from `SENDER_EMAILS` and lists them.

Tailored for UberEats receipts, it draws a bar plot with keys being the month and year in format `YYYY-MM` and
the values being the total of expenses payed for that month.

```
poetry run uber_eats_stats --sender-email=<SENDER_EMAILS> --keywords=<KEYWORDS>
```

Example:
```bash
poetry run uber_eats_stats --sender-email='uber.portugal@uber.com' --keywords='Total'
```

## Save UberEats Expenses to Json

Filters available messages with keyword `Total` and from sender email `uber.portugal@uber.com` and lists them.

Scraps data from those messages to populate a `UberEatsExpense` objects that will then be serialized to a Json file.

```
poetry run uber_eats_save_expenses --output-filepath=<OUTPUT_FILEPATH>
```

Example:
```bash
poetry run uber_eats_save_expenses --output-filepath='./gmail_fisher/output/uber_eats_expenses.json'
```