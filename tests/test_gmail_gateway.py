from gmail_fisher.api.gateway import GmailGateway


def test_get_email_messages(gmail_api_stub):
    messages = GmailGateway.list_message_ids(
        sender_emails="portugal-food@bolt.eu", keywords="Delivery", max_results=10
    )
    print(len(messages))
