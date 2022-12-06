import os, requests, csv
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

venues = ["EMO'S", "SCOOT INN"]
output = []

def compile_info():
    dates = soup.find_all('meta', itemprop = 'startDate')
    doors = soup.find_all('span', itemprop = 'doorTime')
    i = 0
    for artist in artists:
        if i >= 0 and i < len(artists):
            start_date = (datetime.strptime(dates[i]['content'][0:10], '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
            combined = []
            if "MOVED TO" in artist.get_text():
                doors.insert(i, "N/A")
                doors_time = "N/A"
                call_time = "N/A"
                end_time = "N/A"
                end_date = "N/A"
            else:
                doors_time = doors[i].get_text()[15:].lstrip()
                call_time = (datetime.strptime(doors_time, '%I:%M %p') - timedelta(hours=1)).strftime('%I:%M %p')
                end_datetime = (datetime.strptime(start_date + " " + doors_time, '%Y-%m-%d %I:%M %p') + timedelta(hours=5)).strftime('%Y-%m-%d %I:%M %p')
                end_time = end_datetime[end_datetime.index(" "):].lstrip()
                end_date = end_datetime[0:end_datetime.index(" ")]
            combined.extend([artist.get_text(), start_date, call_time, end_time, end_date, location])
            combined.append(("Doors: " + doors_time + "\nVenue: " + venue + "\nMerch Coordinator: ").upper())
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
    # print(soup)
    artists = soup.find_all('h2', itemprop='name')
    compile_info()

for combos in output:
    print(combos)

header = ['Subject', 'Start Date', 'Start Time', 'End Time', 'End Date', 'Location', 'Description_1', 'Merch Coordinator', 'Description']

# The following will generate calendar.csv in the same folder where this script is located.

with open('calendar.csv', 'w', encoding='UTF8') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    for combo in output:
        writer.writerow(combo)
print()
print("Exported to " + os.getcwd() + "/calendar.csv")
print()