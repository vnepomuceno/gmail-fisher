# Gmail Fisher

![Build Status](https://api.travis-ci.com/Vnepomuceno/gmail-fisher.svg?branch=master)

Automation scripts for interacting with Gmail API 🎣

## Save Attachments

Filters available messages with `KEYWORDS` and from `SENDER_EMAILS` and lists them.

When the `--download-pdf` flag is inputted, if filtered messages contain attachments, then those will be downloaded
to an `output` directory and with a formatted name of `PaySlip_YYYY-MM.pdf`.

```
$ python run.py save_attachments <SENDER_EMAILS> <KEYWORDS> --download-pdf
```

Example:
```bash
$ python run.py save_attachments 'me@my-company.com|payroll@my-company.com' 'payslip' --download-pdf
```

## Plot Expenses

Filters available messages with `KEYWORDS` and from `SENDER_EMAILS` and lists them.

Tailored for UberEats receipts, it draws a bar plot with keys being the month and year in format `YYYY-MM` and
the values being the total of expenses payed for that month.

```
$ python run.py stats <SENDER_EMAILS> <KEYWORDS> --download-pdf
```

Example:
```bash
$ python run.py stats 'uber.portugal@uber.com' 'Total'
```
