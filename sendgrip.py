import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_email(sendgrid_api_key, from_email, to_email, subject, content):
    message = Mail(
        from_email=from_email,
        to_emails=to_email,
        subject=subject,
        html_content=content
    )

    try:
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)
        print(f"Email sent successfully: {response.status_code}")
    except Exception as e:
        print(f"Error sending email: {e}")

if __name__ == "__main__":
    sendgrid_api_key = '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'
    from_email = 'kunaal.umrigar@ucdconnect.ie'
    to_email = 'raamesh.kandalgaonkar@ucdconnect.ie'
    subject = 'Test Email'
    content = '<strong>This is a test email sent using SendGrid API</strong>'

    send_email(sendgrid_api_key, from_email, to_email, subject, content)
