# Merch Coordinator Automator

This repository is for the work I do at the LiveNation venues Emo's and the Historic Scoot Inn in Austin, TX.

The `calendar_generator.py` script in this repo will scrape the calendars on the [Emo's ](https://www.emosaustin.com/events-calendar) and [Scoot Inn](https://scootinnaustin.com/calendar) websites to generate CSV with the information needed to create the schedule for the Merch Coordinators. It is generated in a format that can then be quickly modified and imported into Google Calendar using [the format expressed in the documentation here](https://support.google.com/calendar/answer/37118?hl=en&co=GENIE.Platform%3DDesktop#zippy=%2Ccreate-or-edit-a-csv-file).

### Instructions

To get started, you'll need to setup a virtual environment using Python 3 and activating it to install the neccesary dependencies. The only dependency the first version of this script uses is `beautifulsoup4 4.11.1`, and I'm using Python 3.11.0 in Windows 10.

```
python -m venv .venv
. .\.venv\Scripts\activate
pip install -r requirements.txt
```

To activate your `venv` in Linux or Mac, use:

```
. .venv/bin/activate
```

From here, you should be good to run the script:

```
python calendar_generator.py
```

This will generate a `calendar.csv` in your folder that is included in the `.gitignore` so it doesn't get pushed to the repo. I'm actively working on updating this script to expand.