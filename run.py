import sys

from gmail_fisher.save_attachments import gmail_save_attachments
from gmail_fisher.stats import plot_uber_eats_expenses

if sys.argv[1] == "save_attachments":
    gmail_save_attachments(sys.argv)
elif sys.argv[1] == "stats":
    plot_uber_eats_expenses(sys.argv)
else:
    print(f"❌  Unrecognized command to run '{sys.argv[1]}'")
