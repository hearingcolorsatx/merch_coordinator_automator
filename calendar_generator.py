import os, requests, csv
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

venues = ["EMO'S", "SCOOT INN"]
output = []
table = []

def compile_info():
    dates = soup.find_all('meta', itemprop = 'startDate')
    doors = soup.find_all('span', itemprop = 'doorTime')
    now = datetime.now()
    first_next_month = (now + timedelta(days=30)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    # print(first_next_month)
    first_after_next = (now + timedelta(days=60)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    # print(first_after_next)

    i = 0
    for artist in artists:
        start_date = datetime.strptime((datetime.strptime(dates[i]['content'][0:10], '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d'), '%Y-%m-%d')
        # print(start_date)
        if start_date >= first_next_month and start_date < first_after_next:
            # print(start_date)
            if i >= 0 and i < len(artists):
                email_table = []
                combined = []
                if "MOVED TO" in artist.get_text():
                    doors.insert(i, "N/A")
                    doors_time = "N/A"
                    call_time = "N/A"
                    end_time = "N/A"
                    end_date = "N/A"
                else:
                    doors_time = datetime.strptime(doors[i].get_text()[15:].lstrip(), '%I:%M %p')
                    call_time = (doors_time - timedelta(hours=1))
                    end_dt = datetime.combine(start_date.date(), doors_time.time()).strftime('%Y-%m-%d %I:%M %p')
                    end_datetime = (datetime.strptime(end_dt, '%Y-%m-%d %I:%M %p') + timedelta(hours=5)).strftime('%Y-%m-%d %I:%M %p')
                    end_time = end_datetime[end_datetime.index(" "):].lstrip()
                    end_date = end_datetime[0:end_datetime.index(" ")]
                email_table.extend([start_date.date(), artist.get_text(), call_time.time().strftime("%I:%M %p"), venue])
                table.append(email_table)
                combined.extend([start_date.date(), artist.get_text(), call_time.time().strftime("%I:%M %p"), end_time, end_date, location])
                combined.append(("Doors: " + doors_time.time().strftime("%I:%M %p") + "\nVenue: " + venue + "\nMerch Coordinator: ").upper())
                output.append(combined)
        i += 1

for venue in venues:
    if venue == "EMO'S":
        url = requests.get("https://www.emosaustin.com/events-calendar")
        location = "2015 E Riverside Dr, Austin, TX 78741"
    elif venue == "SCOOT INN":
        url = requests.get("https://scootinnaustin.com/calendar")
        location = "1308 E 4th St, Austin, TX 78702"
    else:
        print("No more venues! Check your venue list because you shouldn't see this!")

    soup = BeautifulSoup(url.content, 'html.parser')
    artists = soup.find_all('h2', itemprop='name')
    compile_info()

for combos in output:
    print(combos)

header = ['Start Date', 'Subject', 'Start Time', 'End Time', 'End Date', 'Location', 'Description_1', 'Merch Coordinator', 'Description']
email_header = ['Start Date', 'Subject', 'Start Time', 'Venue']

# The following will generate email_table.csv in the same folder where this script is located. This is the table that will be emailed to the Merch Coordinators.
with open('csv_files/email_table.csv', 'w', encoding='UTF8') as f:
    writer = csv.writer(f)
    writer.writerow(email_header)
    for show in table:
        writer.writerow(show)

# The following will generate calendar.csv in the same folder where this script is located. This is the actual calendar that wil be used to create the schedule and can be imported in Google Calendars.
with open('csv_files/calendar.csv', 'w', encoding='UTF8') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    for combo in output:
        writer.writerow(combo)
print()
print("Exported to " + os.getcwd() + "csv_files/calendar.csv")
print()