from gmail_fisher.io import FileUtils


def test_get_payslip_filename():
    subject = (
        "Please note that the Payslip for the income earned in 8-2020 is attached."
    )
    expected = "PaySlip_2020-8.pdf"
    filename = FileUtils.get_payslip_filename(subject)

    assert filename == expected
