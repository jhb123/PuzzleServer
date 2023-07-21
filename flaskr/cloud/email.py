import boto3


class EmailStrings:
    sender_address = "crosswordapp26@gmail.com"

    reset_subject = "Reset Code for CrosswordScan"
    reset_body = "Your reset code for CrosswordScan is:\n{0}\n" \
                 "If you didn't request this, you may ignore this email."


class EmailManager:

    def __init__(self):
        self.ses_client = boto3.client("ses", region_name="eu-north-1")
        self.CHARSET = "UTF-8"

    def send_reset_code(self, recipient_email, code):
        destination = {"ToAddresses": [recipient_email]}
        message = {
            "Body": {
                "Text": {
                    "Charset": self.CHARSET,
                    "Data": EmailStrings.reset_body.format(code),
                }
            },
            "Subject": {
                "Charset": self.CHARSET,
                "Data": EmailStrings.reset_subject,
            },
        }
        source = EmailStrings.sender_address

        self.ses_client.send_email(
            Destination=destination,
            Message=message,
            Source=source
        )
