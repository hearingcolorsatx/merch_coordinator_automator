# Merch Coordinator Automator v4.0

The Merch Coordinator Automator was created specifically for the LiveNation venues Emo's and the Historic Scoot Inn in Austin, TX to assist in the creation of the schedule for the Merch Coordinators. The original implementation of this project was just the `calendar_generator.py` script, which would produce a `csv` called `calendar.csv` that contained the information for all shows on the Emo's and Scoot Inn event pages.

This has since been expanded to include scripts that will take that information and email a table of the shows for next month to all the Merch Coordinators. Scripts have been added to use either Gmail or Outlook365, but does require access to Google Cloud for GMail and/or Azure for O365 depending on your preference. In this version, the event dates are no longer retrieved using `dates = soup.find_all('meta', itemprop = 'startDate')`, but rather by the `eventMonth` and `eventDay` tags with some additional logic for improved accuracy for the event dates.

## Summary

`cal_emailer_gmail.py` and `cal_emailer_o365.py` will invoke `calendar_generator.py`, which will scrape the calendars on the [Emo's ](https://www.emosaustin.com/events-calendar) and [Scoot Inn](https://scootinnaustin.com/calendar) websites to generate a `csv` file with the information needed to create the schedule for the Merch Coordinators - `csv_files/calendar.csv`. This file is included in the `.gitignore`.

`csv_files/calendar.csv` is generated in a format that can be quickly modified and imported into Google Calendar using [the format expressed in the documentation here](https://support.google.com/calendar/answer/37118?hl=en&co=GENIE.Platform%3DDesktop#zippy=%2Ccreate-or-edit-a-csv-file).

### GET THE COOKIE - REQUIRED!!!

The way the script was previously structured led to some errors that essentially rendered the script completely ineffective, so it had to be restructured to account for some missing data - more specifically missing doors times. Logic was added to take the link from the `Buy Tickets` button and parse that ticket info page for the doors time.

However, to do this requires authentication in the form of a cookie retrieved from the request headers. While getting that cookie was unsuccessfully attempted through code, for the time being, it has to be done manually. To do this, follow these steps:

1. Open your browser with developer tools up and the `Network Tab` selected
2. Navigate to https://www.emosaustin.com/events-calendar
3. Click any of the `Buy Tickets` buttons and make sure it directs you to `concerts.livenation.com` page
4. Locate `tmauthadaptor.js` on the left side of the developer tools and click it 
5. Collapse `General` and `Response Headers` or scroll down to `Request Headers`
6. Highlight the entire cookie and copy it
    - It begins with `mt.v=...` and ends at the line above `Host: identity.livenation.com`
7. Open `/config_files/sample_parameters.json` and replace `COOKIE_FROM_LIVENATION` with the cookie by pasting it
    - The cookie is good for about 5 minutes at which point you'll have to hit refresh so keep that page open if necessary!

FAILURE TO COMPLETE THE ABOVE STEPS WILL RESULT IN THE FOLLOWING ERROR:

```
  File "merch_coordinator_automator/calendar_generator.py", line 191, in format_times     
    unformatted_doors_time = datetime.strptime(doors_time, "%I:%M %p")
                             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: strptime() argument 1 must be str, not None
```

That's because TicketMaster and `concerts.livenation.com` require the authentication provided by that cookie. Otherwise, `date_div = ticket_info.find('div', class_='event-header__event-date')` will come back `None`, and that is exactly what the error is pointing out. At this point, you're good to continue running the script!

If you'd just like to run the `calendar_generator.py` script, complete the top of the `Getting Started` up through `pip install -r requirements.txt`, and simply execute:

`python calendar_generator.py`

This will run just that script and display the shows at both venues for next month as well as the concurrent shows. To send an email that uses that script to prepare and communicate that info to the team, continue on.

## Getting started

To get started, you'll need to setup a virtual environment using Python 3 and activate it to install the necessary dependencies like such:

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

`requirements.txt` has all the necessary dependencies and indicates which script uses which dependencies. 

### Setup `emails.json`

You'll need to create the file `./config_files/emails.json` to put the necessary email addresses in the scripts. There is a difference in the formats for `recipients` and `cc` between Outlook365 and Gmail that will be discussed below. The file will be invoked in the scripts using the following:

```
emails = json.load(open("config_files/emails.json"))
```

This will allow you to call the sender, recipients, and any ccs using the following syntax for Gmail:

```
to = emails["gmail_recipients"]
cc = emails["gmail_cc"]
sender = emails["sender"]
```

And the following syntax for Outlook365 (there's no need to specify the sender):

```
"toRecipients": emails["recipients"],
"ccRecipients": emails["cc"]
```

I have included `./config_files/sample_emails.json` so the user could use that as a template and rename to `emails.json`. For `sender`, simply provide your own email (regardless of what is provided, it will show the sender as the email account that was authenticated in this workflow). The following information explains the format in which to provide the `recipients` and `cc's` for both Gmail and Outlook365.

For Gmail, provide a list of emails for the intended recipients for `gmail_recipients` separated by commas, e.g. `"user1@email.com, user2@email.com, user3@email.com", etc`. Similarly, provide a list of emails for `gmail_cc` in the same format (if applicable).

However, for Outlook365, the `recipients` and `cc's` will be provided in the following format:

```
    "recipients": [
        {
            "emailAddress": {
                "address": "user@email.com"
            }
        },
        {
            "emailAddress": {
                "address": "user1@email.com"
            }
        }
    ],
    "cc": [
        {
            "emailAddress": {
                "address": "user3@email.com"
            }
        },
        {
            "emailAddress": {
                "address": "user4@email.com"
            }
        }
    ]
```

Simply use `config_files\sample_emails.json` as a template and modify as needed!

### For `cal_emailer_gmail.py`

For this implementation, I have 2FA enabled on my account. `cal_emailer_gmail.py` was taken and modified from [this post on StackOverflow](https://stackoverflow.com/a/43379469). You will need access to the Google Cloud Platform (GCP) for authentication in order to execute this script. Once you have access to https://console.cloud.google.com/, execute the following steps:

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

2. Enter Name, Supported Account Types (for this implementation, I used Accounts in any organizational directory (Any Azure AD directory - Multi-tenant) and personal Microsoft accounts (e.g. Skype, Xbox)), any Redirect URI, and click the Register Button. 

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

A browser window will open up for you to authenticate your machine. Just follow the instructions, and once you've logged into your account you'll be directed to your Outlook365 inbox - keep this window open for 15 seconds after which the email will be sent to the specified recipients. If you're already logged into your account, it may just take you right to your inbox so just give the scripts a few seconds to finish running.

If for some reason, you're having network issues, and 15 seconds isn't long enough for the script to authenticate and log in, update line 33 in the `cal_emailer_o365.py` script:

```
time.sleep(15)
```

## TROUBLESHOOTING

### ISSUE:

When working on version 2 of this script, I noticed in February and March of 2023 that it appeared to be skipping over events happening on the first of the month. While there was no error to indicate why this was happening because the script was technically working correctly, the following variables establishing the first of the next two months had to be adjusted:

```
    first_next_month = (now + timedelta(days=30)).replace(day=1)
    first_after_next = (now + timedelta(days=60)).replace(day=1)
```

The reason for this was because the `startDate` in the `html` output appears in the following format: `2023-03-01T00:00:00.000Z`. The timestamps are usually `00:00:00.000Z` as shown in the example so this meant that if I set `first_next_month = (now + timedelta(days=30)).replace(day=1)`, the timestamp for the first of next month would be set to at whatever time I ran the script. For example, if I ran the script mid-February sometime around 4:15 PM, then `first_next_month = 2023-03-01T16:15:23:000Z`, and if the `startDate` for an event on the first of next month is `2023-03-01T00:00:00.000Z`, this means that when the script will skip that event entirely when executing the following logic: `if start_date >= first_next_month.date() and start_date < first_after_next.date():`.

### SOLUTION:

For this reason, the `first_next_month` and `first_after_next` variables had been updated to the following:

```
    first_next_month = (now + timedelta(days=30)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    first_after_next = (now + timedelta(days=60)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
```

This has been resolved and should not present any issues - this is strictly for documentation purposes.

### ISSUE:

I encountered the following error while preparing the calendar and schedule for August 2023:

```
    doors_time = datetime.strptime(doors[i].get_text()[15:].lstrip(), '%I:%M %p')
                                   ~~~~~^^^
IndexError: list index out of range
```

### EXPLANATION

After reviewing the script carefully, I couldn't see any issue with the script itself and printed out the doors variable: `print(doors)`. I noticed that there were only 5 door times listed for all the shows listed at the Scoot Inn Event Calendar Page, and upon visiting the site, noticed that there were only door times listed for 5 events. Furthermore, since the door times are for 5 events over several months, the times would not align correctly with the other event details because of how the script is structured. This has been resolved in version 4 of this application by adding the find_doors_time() function, which utilizes the `Buy Tickets` link to get the doors time directly from the ticket information page via TicketMaster/concerts.livenation.

### SOLUTION

As a workaround for version 3 of this application, the logic - `if i >= 0 and i < len(artists):` - had been updated and expanded to:

```
if i >= 0 and i < len(doors) and i < len(artists):
... (omitted code for brevity)

else:
    # Handle the case when the index i is out of range for doors or artists
    print("\n!!! INDEX OUT OF RANGE FOR DOORS OR ARTISTS:", i, "!!!\n")
    print("What does this mean? This means that there most likely may be some data missing so you'll want to check over your csv files and first make sure that all your events are listed. Next, make sure all the event dates and doors time are correct to the event as listed on the venues' event calendar webpages. Add any events that may have gotten skipped and adjust any door times as needed.\n")

```

This is no longer an issue in version 4 of this application as the script has been entirely refactored. Just be sure you're getting all the data you need and always double check the information!

That's it for now - this should cover everything to generate the calendar and create the merch coordinator schedule for next month!