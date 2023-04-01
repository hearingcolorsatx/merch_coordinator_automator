# Merch Coordinator Automator

This repository is for the work I do at the LiveNation venues Emo's and the Historic Scoot Inn in Austin, TX. I simply created this project to improve my Python skills, and assist with my tasks as the manager for the Merch Coordinators. The original implementation of this project was just the `calendar_generator.py` script, which would produce a `csv` called `calendar.csv` that contained the information for all shows on the Emo's and Scoot Inn calendars found on their respective websites. This has since been expanded to include scripts that will take that information and email a table of just the shows for next month to all the Merch Coordinators using either GMail or Outlook 365.

## Summary

`cal_emailer_gmail.py` and `cal_emailer_o365.py` will invoke `calendar_generator.py`, which will scrape the calendars on the [Emo's ](https://www.emosaustin.com/events-calendar) and [Scoot Inn](https://scootinnaustin.com/calendar) websites to generate a couple of `csv` files with the information needed to create the schedule for the Merch Coordinators. In the process, there will be 2 files created that are included in the `.gitignore` - `email_table.csv` and `calendar.csv`.

`email_table.csv` will be used to email the Merch Coordinators the shows coming up next month that need to be staffed with just the date, artist, time, and venue. `calendar.csv` is a little more expansive and generated in a format that can then be quickly modified and imported into Google Calendar using [the format expressed in the documentation here](https://support.google.com/calendar/answer/37118?hl=en&co=GENIE.Platform%3DDesktop#zippy=%2Ccreate-or-edit-a-csv-file).

## Getting started

To get started, you'll need to setup a virtual environment using Python 3 and activate it to install the neccesary dependencies like such:

In Windows, use:

```
python -m venv .venv
. .\.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

In Linux or Mac, use:

```
python -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

`requirements.txt` has all the necessary dependencies and indicates which script uses which depencies. 

### Setup `emails.json`

You'll need to create the file `emails.json` in the `./config_files` directory to put the necessary email addresses in the scripts. The file will be invoked in the scripts using the following:

```
emails = json.load(open("config_files/emails.json"))
```

This will allow you to call the sender, recipients, and any ccs using the following syntax:

```
sender = emails["sender"]
to = emails["recipients"]
cc = emails["cc"]
```

I have included `./config_files/sample_emails.json` so the user could use that as a template and rename to `emails.json`. Provide a list of the `recipients'` separated by commas, e.g. user1@email.com, user@email.com, user@email.com. For `sender`, simply provide your own email (regardless of what is provided, it will show the sender as the email account that was authenticated in this workflow). You can also provide addresses in the `cc` similarly to how the recipients are done.

### For `cal_emailer_gmail.py`

For this implementation, I have 2FA enabled on my account. `cal_emailer_gmail.py` was taken and modified from [this post on StackOverflow.](https://stackoverflow.com/a/43379469). You will need access to the Google Cloud Platorm (GCP) for authentication in order to execute this script. Once you have access to https://console.cloud.google.com/, execute the following steps:

1. [Navigate here to enable the api you need](https://console.developers.google.com/apis/)

2. [Once enabled, select Credentials](https://console.cloud.google.com/apis/credentials)

3. Select Create Credentials > OAuth client ID

4. Select Application Type, enter the Name you'd like to use, and click the Create Button.

5. In the popup that appears afterward, select DOWNLOAD JSON.

6. Rename that json to `credentials.json` and move it to the `./config_files` folder. NOTE: `credentials.json` is included in the `.gitignore` so as to avoid pushing sensitive information into the repo when you complete these steps.

Once everything is in place, simply execute:

```
python cal_emailer_gmail.py
```

A browser window will open up for you to authenticate your machine. Just follow the instructions after which, you should be good to go and the email will be sent to the specified recipients!

### For `cal_emailer_o365.py`

For this implementation, I have 2FA enabled on my account. You will need access to the Microsoft Azure for authentication in order to execute `cal_emailer_o365.py`. Once you have access to https://portal.azure.com/, execute the following steps:

1. [Navigate here to create an app registration](https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationsListBlade)

2. Enter Name, Supported Account Types (for this implementation, I used Accounts in any organizational directory (Any Azure AD directory - Multitenant) and personal Microsoft accounts (e.g. Skype, Xbox)), any Redirect URI, and click the Register Button. 

3. Once directed to the app registration Overview page, copy the `client_id` and the `tenant_id` and paste them over `CLIENT_ID` and `TENANT_ID` respectively in `./config_files/sample_parameters.json`.

4. In the Azure Portal, click the Certificates & secrets blade and select the +New client secret Button.

5. Enter a description and select a time frame for the secret to expire (I usually set the expiration for 90 days).

6. Once the secret is created, copy the Value of that secret, and paste it over the `CLIENT_SECRET` in `./config_files/sample_parameters.json`.

7. Finish populating the remaining values in `./config_files/sample_parameters.json`. For my use case, I was able to use the following:

```
    "auth_endpoint": "https://login.microsoftonline.com/TENANT_ID/oauth2/v2.0/authorize",
    "redirect_uri": "https://outlook.office.com/mail/",
    "scope": "Mail.Send",
    "token_endpoint": "https://login.microsoftonline.com/TENANT_ID/oauth2/v2.0/token"

```

8. Rename `sample_parameters.json` to `parameters.json`.

Once everything is in place, simply execute:

```
python cal_emailer_o365.py
```

A browser window will open up for you to authenticate your machine. Just follow the instructions, and once you've logged into your account you'll be directed to your Outlook inbox - keep this window open for 15 seconds after which the email will be sent to the specified recipients!

If for some reason, you're having network issues, and 15 seconds isn't long enough for the script to authenticate and log in, update line 33 in the `cal_emailer_o365.py` script:

```
time.sleep(15)
```

And that's it for now - this should cover everything to generate the calendar and create the merch coordinator schedule for next month!
