# Merch Coordinator Automator

This repository is for the work I do at the LiveNation venues Emo's and the Historic Scoot Inn in Austin, TX. I simply created this project to improve my Python skills, and assist with my tasks as the manager for the Merch Coordinators. The original implementation of this project was just the `calendar_generator.py` script, which would produce a `csv` called `calendar.py` that contained the information for all shows on the Emo's and Scoot Inn calendars found on their respective websites. This has since been expanded to include scripts that will take that information and email a table of just the shows for next month to all the Merch Coordinators.

## Getting started

At the moment, I'm using Python 3.11.0 in Windows 10 to build out this script. To get started, you'll need to setup a virtual environment using Python 3 and activate it to install the neccesary dependencies like such:

```
python -m venv .venv
. .\.venv\Scripts\activate
pip install -r requirements.txt
```

To activate your `venv` in Linux or Mac, use:

```
. .venv/bin/activate
```

For this implementation, I have 2FA enabled on my account account. You will need access to the Google Cloud Platorm (GCP) for authentication in order to execute `quickstart.py` and `calendar_emailer.py`. `quickstart.py` will simply authenticate your machine so that the email with the table for all shows next month can be sent successfully. Otherwise, you will run into authentication issues when executing `calendar_emailer.py`.

Rather than reinventing the wheel in order to explain how to authenticate your machine using GCP, simply refer to [this documentation here](https://developers.google.com/gmail/api/quickstart/python). This will cover how to enable the API, authorize credentials for a desktop application, install the Google client library, configure and run the script. The section covering [how to install the Google client library](https://developers.google.com/gmail/api/quickstart/python#install_the_google_client_library) can be skipped as it is covered above when setting up the `venv`. 

`requirements.txt` has all the necessary dependencies and indicates which script uses which depencies. You will also notice that the official documentation from Google is from where I obtained `quickstart.py`. When you complete these steps, you will have a file called `credentials.json` that you need to copy to the root of this repo. It's included in the `.gitignore` so as to avoid pushing sensitive information into the repo.

Once everything is in place, simply execute:

```
python quickstart.py
```

A browser window should open up for you to authenticate your machine. Just follow the instructions after which, you should be good to go!

### Instructions

Once you've completed the above steps, you'll need to create the files `email_recipients.txt` and `email_sender.txt`. In `email_recipients.txt`, you will provide a list of the recipients emails on a single line separated by commas. e.g. email1@domain.com, email2@domain.com, email3@domain.com. In `email_sender.txt` you will simply provide your email, but regardless of what is provided, it will show the sender as the email account that was authenticated in this workflow. Both `txt` files are also included in the `.gitignore` so that no one's private email is pushed to the repo. Now, you will simply be able to execute the following:

```
python calendar_emailer.py
```

The `calendar_emailer.py` will invoke `calendar_generator.py`, which will scrape the calendars on the [Emo's ](https://www.emosaustin.com/events-calendar) and [Scoot Inn](https://scootinnaustin.com/calendar) websites to generate a `csv` file with the information needed to create the schedule for the Merch Coordinators. In the process, there will be 2 files created that are included in the `.gitignore` so as to not push to the repo - `email_table.csv` and `calendar.csv`.

`email_table.csv` will be used to email the Merch Coordinators the shows coming up next month that need to be staffed with just the date, artist, time, and venue. `calendar.csv` is a little more expansive and generated in a format that can then be quickly modified and imported into Google Calendar using [the format expressed in the documentation here](https://support.google.com/calendar/answer/37118?hl=en&co=GENIE.Platform%3DDesktop#zippy=%2Ccreate-or-edit-a-csv-file).

And that's it for now - this should cover everything to generate the calendar and create the merch coordinator schedule for next month!
