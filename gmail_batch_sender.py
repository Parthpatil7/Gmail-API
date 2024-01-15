import os
import base64
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Define the sender's email address
sender_email = " "

# Define the path to the credentials file
credentials_file = "credentials.json"

# Define the path to the recipients file
recipients_file = "recipients.txt"

# Define the batch size (e.g., 100 recipients per batch)
batch_size = 100

# Load recipients from the file
with open(recipients_file, "r") as file:
    recipients = [line.strip() for line in file.readlines()]

# Load credentials from the file
creds = None
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json')

# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    flow = InstalledAppFlow.from_client_secrets_file(credentials_file, ["https://www.googleapis.com/auth/gmail.compose"])
    creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

# Build the Gmail API service
service = build("gmail", "v1", credentials=creds)

# Prompt the user for the batch number
while True:
    try:
        batch_number = int(input("Enter the batch number (1, 2, 3, ...): "))
        if batch_number < 1:
            print("Batch number must be greater than or equal to 1.")
        else:
            break
    except ValueError:
        print("Invalid input. Please enter a valid batch number.")

# Calculate the range of recipients for the specified batch
start_index = (batch_number - 1) * batch_size
end_index = batch_number * batch_size

# Ensure the batch is within the bounds of the recipient list
if start_index < 0:
    start_index = 0
if end_index > len(recipients):
    end_index = len(recipients)

# Define the email message
message_text = f"""

"""

# Send the email to recipients in the specified batch
for recipient_email in recipients[start_index:end_index]:
    email = MIMEMultipart()
    email["Subject"] = "Subject"
    email.attach(MIMEText(message_text, "plain"))
    email["To"] = recipient_email

    message = {"raw": base64.urlsafe_b64encode(email.as_bytes()).decode("utf-8")}

    try:
        message = service.users().messages().send(userId="me", body=message).execute()
        print(f"Email sent to {recipient_email} successfully.")
    except HttpError as error:
        print(f"An error occurred while sending the email to {recipient_email}: {error}")
        error_details = json.loads(error.content)
        if 'error' in error_details and 'message' in error_details['error']:
            print(f"Error message: {error_details['error']['message']}")
        if 'error' in error_details and 'code' in error_details['error']:
            print(f"Error code: {error_details['error']['code']}")
