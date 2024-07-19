import os
import base64
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, Disposition, FileContent, FileName, FileType

def encode_image_to_base64(image_path):
    with open(image_path, 'rb') as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode()
    return encoded_image

def send_email(sendgrid_api_key, from_email, to_emails, subject, content, image_path):

    encoded_image = encode_image_to_base64(image_path)
    attached_image = Attachment(
        FileContent(encoded_image),
        FileName(os.path.basename(image_path)),
        FileType('image/png'),  # Change to the appropriate MIME type if needed
        Disposition('inline'),
        content_id='welcome_image'
    )

    message = Mail(
        from_email=from_email,
        to_emails=to_emails,
        subject=subject,
        html_content=content
    )

    message.add_attachment(attached_image)

    try:
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)
        print(f"Email sent successfully: {response.status_code}")
    except Exception as e:
        print(f"Error sending email: {e}")

if __name__ == "__main__":
    sendgrid_api_key = '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'
    from_email = 'kunaal.umrigar@ucdconnect.ie'
    to_emails = ['kunaal.umrigar@ucdconnect.ie']
    subject = 'Test Email'
    user_name = input("Enter the recipient's name: ")
    content = f'''
    <html>
        <body>
            <div style="font-family: Arial, sans-serif; line-height: 1.6;">
                <h2 style="color: #4CAF50;">Hello {user_name}!</h2>
                <p>This is a test email sent using the <strong>SendGrid API</strong> to multiple recipients.</p>
                <p>Below is an image included in the email:</p>
                <img src="cid:welcome_image" alt="Welcome Image" style="width:100%; max-width:600px;"/>
                <p>Thank you!</p>
                <p>Best regards,<br>Kunaal</p>
            </div>
        </body>
    </html>
    '''

    image_path = '/Users/kunaalumrigar/Desktop/welcome.png'

    send_email(sendgrid_api_key, from_email, to_emails, subject, content, image_path)
