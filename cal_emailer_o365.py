import csv, json, logging, pyautogui, pyperclip, requests, time, webbrowser

from calendar_generator import *
from tabulate import tabulate
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs

logging.basicConfig(level=logging.ERROR)

config = json.load(open("config_files/parameters.json"))
emails = json.load(open("config_files/emails.json"))

# Define the request parameters
authorize_endpoint = config["auth_endpoint"]
client_id = config["client_id"]
client_secret = config["client_secret"]
redirect_uri = config["redirect_uri"]
scope = config["scope"]
token_endpoint = config["token_endpoint"]

# Generate the authorization URL
auth_url = authorize_endpoint + "?" + "response_type=code" + "&" + "client_id=" + client_id + "&" + "redirect_uri=" + redirect_uri + "&" + "scope=" + scope

# Open the authorization URL in the default browser
webbrowser.open(auth_url)

# Wait for the user to complete the sign-in process and return to the redirect URI
redirect_uri_path = urlparse(redirect_uri).path
authorization_code = None

while authorization_code is None:
    # Wait 15s for page to load while user logs in (adjust as needed)
    time.sleep(15)
    # Press Ctrl + L to focus on URL bar (Keep browser window open on redirect page and selected!!)
    pyautogui.hotkey('ctrl', 'l')
    # Press Ctrl + C to copy URL
    pyautogui.hotkey('ctrl', 'c')
    # Get URL from clipboard
    url = pyperclip.paste()

    # Parse the code from the url string
    query_string = urlparse(url).query
    query_params = parse_qs(query_string)
    if "code" in query_params and redirect_uri_path in urlparse(url).path:
        authorization_code = query_params["code"][0]

# Exchange the authorization code for an access token
response = requests.post(token_endpoint, data={
    "grant_type": "authorization_code",
    "client_id": client_id,
    "client_secret": client_secret,
    "code": authorization_code,
    "redirect_uri": redirect_uri,
    "scope": scope
})

# Parse the response to obtain the access token
if response.status_code == 200:
    access_token = json.loads(response.text)["access_token"]
    print("Access token:", access_token)
else:
    print("Error:", response.status_code, response.text)

# Set the API endpoint URL for sending email
api_url = 'https://graph.microsoft.com/v1.0/me/sendMail'

# Set the access token in the Authorization header
headers = {'Authorization': 'Bearer ' + access_token,
           'Content-Type': 'application/json'}

next_month = (datetime.now() + timedelta(days=30)).strftime("%B")

compile_info()

with open('csv_files/email_table.csv') as input_file:
    reader = csv.reader(input_file)
    data = list(reader)

# Set the email message properties
payload = {
    "message": {
        "subject": f"{next_month} Calendar for Emo's/Scoot Inn",
        "body": {
            "contentType": "HTML",
            "content": r'''Hi All!<br/><br/>I hope everyone is well. It's that time of the month to start looking ahead to {}. The following shows need to be covered:<br/><br/>{table}
                        <br/>Make note of dates where there are shows at both venues. Let me know if there are specific shows you'd like to work. Otherwise,
                        just let me know your availability and I'll get the schedule put together in the next day or two. As always, it's first come first serve. If you have any questions or concerns,
                        please let me know.<br/><br/>Cheers,<br/>Tim'''.format(next_month, table=tabulate(data, headers="firstrow", tablefmt = "html"))
        },
        "toRecipients": [
            {
                "emailAddress": {
                    "address": emails["recipients"]
                }
            }
        ]
    },
    "saveToSentItems": "true"
}

# Send the email
response = requests.post(api_url, headers=headers, data=json.dumps(payload))

# Check the response status code to see if the email was sent successfully
if response.status_code == 202:
    print("Email sent successfully!")
else:
    print("Failed to send email.", response.text)
