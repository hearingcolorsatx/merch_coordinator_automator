import base64, httplib2, json, oauth2client, os

from oauth2client import client, tools, file
#needed for attachment
import mimetypes
  
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
#List of all mimetype per extension: http://help.dottoro.com/lapuadlp.php  or http://mime.ritey.com/

from apiclient import errors, discovery  #needed for gmail service

# Imports everything from the calendar_generator.py script
from calendar_generator import *

## About credentials
# There are 2 types of "credentials": 
#     the one created and downloaded from https://console.developers.google.com/apis/ (let's call it the client_id) 
#     the one that will be created from the downloaded client_id (let's call it credentials, it will be store in C:\Users\user\.credentials)

        #Getting the CLIENT_ID 
            # 1) enable the api you need on https://console.developers.google.com/apis/
            # 2) download the .json file (this is the CLIENT_ID)
            # 3) save the CLIENT_ID in same folder as your script.py 
            # 4) update the CLIENT_SECRET_FILE (in the code below) with the CLIENT_ID filename


        #Optional
        # If you don't change the permission ("scope"): 
            #the CLIENT_ID could be deleted after creating the credential (after the first run)

        # If you need to change the scope:
            # you will need the CLIENT_ID each time to create a new credential that contains the new scope.
            # Set a new credentials_path for the new credential (because it's another file)

def get_credentials():
    # If needed create folder for credential
    home_dir = os.path.expanduser('~') #>> C:\Users\Me
    credential_dir = os.path.join(home_dir, '.credentials') # >>C:\Users\Me\.credentials   (it's a folder)
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)  #create folder if doesnt exist
    credential_path = os.path.join(credential_dir, 'cred send mail.json')

    #Store the credential
    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()

    if not credentials or credentials.invalid:
        CLIENT_SECRET_FILE = 'config_files/credentials.json'
        APPLICATION_NAME = 'Gmail API Python Send Email'
        #The scope URL for read/write access to a user's calendar data  

        SCOPES = 'https://www.googleapis.com/auth/gmail.send'

        # Create a flow object. (it assists with OAuth 2.0 steps to get user authorization + credentials)
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME

        credentials = tools.run_flow(flow, store)

    return credentials

## Get creds, prepare message and send it
def create_message_and_send(sender, to, cc, subject,  message_text_plain, message_text_html, attached_file):
    credentials = get_credentials()

    # Create an httplib2.Http object to handle our HTTP requests, and authorize it using credentials.authorize()
    http = httplib2.Http()

    # http is the authorized httplib2.Http() 
    http = credentials.authorize(http)        #or: http = credentials.authorize(httplib2.Http())

    service = discovery.build('gmail', 'v1', http=http)

    ## without attachment
    message_without_attachment = create_message_without_attachment(sender, to, cc, subject, message_text_html, message_text_plain)
    send_Message_without_attachment(service, "me", message_without_attachment, message_text_plain)

    ## with attachment
    # message_with_attachment = create_Message_with_attachment(sender, to, subject, message_text_plain, message_text_html, attached_file)
    # send_Message_with_attachment(service, "me", message_with_attachment, message_text_plain,attached_file)

def create_message_without_attachment (sender, to, cc, subject, message_text_html, message_text_plain):
    #Create message container
    message = MIMEMultipart('alternative') # needed for both plain & HTML (the MIME type is multipart/alternative)
    print(type(message))
    print("This is the message:", message)
    message['Subject'] = subject
    message['From'] = sender
    message['To'] = to
    message['cc'] = cc

    #Create the body of the message (a plain-text and an HTML version)
    message.attach(MIMEText(message_text_plain, 'plain'))
    message.attach(MIMEText(message_text_html, 'html'))

    raw_message_no_attachment = base64.urlsafe_b64encode(message.as_bytes())
    raw_message_no_attachment = raw_message_no_attachment.decode()
    body  = {'raw': raw_message_no_attachment}
    return body

def create_Message_with_attachment(sender, to, cc, subject, message_text_plain, message_text_html, attached_file):
    """Create a message for an email.

    message_text: The text of the email message.
    attached_file: The path to the file to be attached.

    Returns:
    An object containing a base64url encoded email object.
    """

    ##An email is composed of 3 part :
        #part 1: create the message container using a dictionary { to, from, subject }
        #part 2: attach the message_text with .attach() (could be plain and/or html)
        #part 3(optional): an attachment added with .attach() 

    ## Part 1
    message = MIMEMultipart() #when alternative: no attach, but only plain_text
    message['to'] = to
    message['cc'] = cc
    message['from'] = sender
    message['subject'] = subject

    ## Part 2   (the message_text)
    # The order count: the first (html) will be use for email, the second will be attached (unless you comment it)
    message.attach(MIMEText(message_text_html, 'html'))
    message.attach(MIMEText(message_text_plain, 'plain'))

    ## Part 3 (attachment) 
    # # to attach a text file you containing "test" you would do:
    # # message.attach(MIMEText("test", 'plain'))

    #-----About MimeTypes:
    # It tells gmail which application it should use to read the attachment (it acts like an extension for windows).
    # If you dont provide it, you just wont be able to read the attachment (eg. a text) within gmail. You'll have to download it to read it (windows will know how to read it with it's extension). 

    #-----3.1 get MimeType of attachment
        #option 1: if you want to attach the same file just specify it’s mime types

        #option 2: if you want to attach any file use mimetypes.guess_type(attached_file) 

    my_mimetype, encoding = mimetypes.guess_type(attached_file)

    # If the extension is not recognized it will return: (None, None)
    # If it's an .mp3, it will return: (audio/mp3, None) (None is for the encoding)
    #for unrecognized extension it set my_mimetypes to  'application/octet-stream' (so it won't return None again). 
    if my_mimetype is None or encoding is not None:
        my_mimetype = 'application/octet-stream' 

    main_type, sub_type = my_mimetype.split('/', 1)# split only at the first '/'
    # if my_mimetype is audio/mp3: main_type=audio sub_type=mp3

    #-----3.2  creating the attachment
        #you don't really "attach" the file but you attach a variable that contains the "binary content" of the file you want to attach

        #option 1: use MIMEBase for all my_mimetype (cf below)  - this is the easiest one to understand
        #option 2: use the specific MIME (ex for .mp3 = MIMEAudio)   - it's a shorcut version of MIMEBase

    #this part is used to tell how the file should be read and stored (r, or rb, etc.)
    if main_type == 'text':
        print("text")
        temp = open(attached_file, 'r')  # 'rb' will send this error: 'bytes' object has no attribute 'encode'
        attachment = MIMEText(temp.read(), _subtype=sub_type)
        temp.close()

    elif main_type == 'image':
        print("image")
        temp = open(attached_file, 'rb')
        attachment = MIMEImage(temp.read(), _subtype=sub_type)
        temp.close()

    elif main_type == 'audio':
        print("audio")
        temp = open(attached_file, 'rb')
        attachment = MIMEAudio(temp.read(), _subtype=sub_type)
        temp.close()            

    elif main_type == 'application' and sub_type == 'pdf':   
        temp = open(attached_file, 'rb')
        attachment = MIMEApplication(temp.read(), _subtype=sub_type)
        temp.close()

    else:                              
        attachment = MIMEBase(main_type, sub_type)
        temp = open(attached_file, 'rb')
        attachment.set_payload(temp.read())
        temp.close()

    #-----3.3 encode the attachment, add a header and attach it to the message
    # encoders.encode_base64(attachment)  #not needed (cf. randomfigure comment)
    #https://docs.python.org/3/library/email-examples.html

    filename = os.path.basename(attached_file)
    attachment.add_header('Content-Disposition', 'attachment', filename=filename) # name preview in email
    message.attach(attachment) 

    ## Part 4 encode the message (the message should be in bytes)
    message_as_bytes = message.as_bytes() # the message should converted from string to bytes.
    message_as_base64 = base64.urlsafe_b64encode(message_as_bytes) #encode in base64 (printable letters coding)
    raw = message_as_base64.decode()  # need to JSON serializable (no idea what does it means)
    return {'raw': raw}

def send_Message_without_attachment(service, user_id, body, message_text_plain):
    try:
        message_sent = (service.users().messages().send(userId=user_id, body=body).execute())
        message_id = message_sent['id']
        # print(attached_file)
        print (f'Message sent (without attachment) \n\n Message Id: {message_id}\n\n Message:\n\n {message_text_plain}')
        # return body
    except errors.HttpError as error:
        print (f'An error occurred: {error}')

def send_Message_with_attachment(service, user_id, message_with_attachment, message_text_plain, attached_file):
    """Send an email message.

    Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me" can be used to indicate the authenticated user.
    message: Message to be sent.

    Returns:
    Sent Message.
    """
    try:
        message_sent = (service.users().messages().send(userId=user_id, body=message_with_attachment).execute())
        message_id = message_sent['id']
        # print(attached_file)

        # return message_sent
    except errors.HttpError as error:
        print (f'An error occurred: {error}')

def main():
    ## Set up the email message properties
    next_month = (datetime.now() + timedelta(days=30)).strftime("%B")     # Get next month for the email subject and body
    event_data = venues_info["EMO'S"]['email_data'] + venues_info["SCOOT INN"]['email_data']          # Import event data

    # Set up table header from the dictionary keys
    table_header = '<tr>' + ''.join([f'<th style="border: 1px solid black;">{key}</th>' for key in event_data[0].keys()]) + '</tr>'

    # Build the rest of the table using dictionary values
    table_rows = ''
    for item in event_data:
        row = '<tr>' + ''.join([f'<td style="border: 1px solid black;">{value}</td>' for value in item.values()]) + '</tr>'
        table_rows += row

    # Assemble the event table in HTML format
    event_table = f"""
    <table style="border: 1px solid black; border-collapse: collapse;">
        <thead>{table_header}</thead>
        <tbody>{table_rows}</tbody>
    </table>
    """

    # Assemble the duplicate show table in HTML format
    show_data = concurrent_shows['shows']
    concurrent_show_rows = ''
    for show in show_data:
        row = '<tr>' + ''.join([f'<td style="border: 1px solid black;">{value}</td>' for value in show]) + '</tr>'
        concurrent_show_rows += row
    dupe_show_table = f"""
    <table style="border-collapse: collapse;">
        <thead>{table_header}</thead>
        <tbody>{concurrent_show_rows}</tbody>
    </table>
    """

    emails = json.load(open("config_files/emails.json"))

    next_month = (datetime.now() + timedelta(days=30)).strftime("%B")
    to = emails["gmail_recipients"]
    cc = emails["gmail_cc"]
    sender = emails["sender"]
    subject = f"{next_month} Calendar for Emo's/Scoot Inn"
    message_text_html  = r'''Hi All!<br/><br/>I hope everyone is well. It's that time of the month to start looking ahead to {}. The following shows need to be covered:<br/>
    <br/>{table}
    <br/> The following is a list of the concurrent shows next month: <br/>
    <br/>{dupes}<br/>
    Let me know if there are specific shows you'd like to work. Otherwise, just let me know your availability and I'll get the schedule put together in the next
    day or two. As always, it's first come first serve.
    <br/><br/>The list of shows in this email is created from what is currently listed on the event calendars of the Emo's and Scoot Inn websites, so there may
    be more shows added at a later date. I will do my best to keep you all informed of any such updates.
    <br/><br/>If you have any questions, please let me know.
    <br/><br/>Cheers,<br/>{sender_name}
    <br/>Emo's/Scoot Inn Merch Coordinator
    <br/>{sender_email} // {sender_number}'''.format(next_month, table=event_table.format(header_cells=table_header, data_rows=table_rows), dupes=dupe_show_table, sender_name=emails["name"], sender_email=emails["sender"], sender_number=emails["number"])
    message_text_plain = '''Hi All! \n \n
    I hope everyone is well. It's that time of the month to start looking ahead to {}. The following shows need to be covered:
    {}
    \n The following is a list of the concurrent shows next month: \n
    \n {} \n
    Let me know if there are specific shows you'd like to work. Otherwise, just let me know your availability and I'll get the schedule put together in the next
    day or two. As always, it's first come first serve.
    \n \n The list of shows in this email is created from what is currently listed on the event calendars of the Emo's and Scoot Inn websites, so there may
    be more shows added at a later date. I will do my best to keep you all informed of any such updates.
    \n \n If you have any questions, please let me know.
    \n \n Cheers,
    \n {}
    \n Emo's/Scoot Inn Merch Coordinator
    \n {} // {}'''.format(next_month, table_rows, dupe_show_table, emails["name"], emails["sender"], emails["number"])

    attached_file = r''
    create_message_and_send(sender, to, cc, subject, message_text_plain, message_text_html, attached_file)

if __name__ == '__main__':
        main()