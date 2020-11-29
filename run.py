print('__file__={0:<35} | __name__={1:<20} | __package__={2:<20}'.format(__file__, __name__, str(__package__)))

import sys
import gmail_fisher.authenticate
from gmail_fisher.save_attachments import gmail_save_attachments

if sys.argv[1] == 'save_attachments':
    gmail_save_attachments(sys.argv)
else:
    print(f"❌  Unrecognized command to run '{sys.argv[1]}'")