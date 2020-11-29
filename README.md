# Gmail Fisher

![Build Status](https://travis-ci.com/Vnepomuceno/gmail-fisher.svg?branch=master)

Automation scripts for interacting with Gmail API 🎣

## Save Attachments

Filters available messages with `KEYWORDS` and from `SENDER_EMAILS` and lists them.

When the `--download-pdf` flag is inputted, if filtered messages contain attachments, then those will be downloaded
to an `output` directory and with a formatted name of `PaySlip_YYYY-MM.pdf`.

```
$ python gmail-save-attachments.py <SENDER_EMAILS> <KEYWORDS> --download-pdf
```

Example:
```bash
$ python gmail-save-attachments.py 'me@my-company.com|payroll@my-company.com' 'payslip' --download-pdf
```
