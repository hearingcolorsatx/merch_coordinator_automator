import requests, re, sys, os, json, csv, time
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

config = json.load(open("config_files/parameters.json"))

# Build the event_data dictionary that will populate venues_info[venue]['event_info']
def create_event_data(event_title, start_date, call_time, doors_time, end_date, end_time, location, venue):
    i = 0
    event_data = {
        'start_date': start_date.strftime('%Y-%m-%d'),
        'subject': event_title,
        'start_time': call_time,
        'end_time': end_time,
        'end_date': end_date,
        'location': location,
        'venue': venue,
        'description': f"=CONCATENATE(I{i + 2},UPPER(J{i + 2}))",
        'description_1': f"DOORS TIME: {doors_time}\n VENUE: {venue}\n MERCH COORDINATOR:",
        'merch_coordinator': None
    }
    venues_info[venue]['event_info'].append(event_data)
    # print(event_data)
    i += 1

    # Create the email_tables
    create_email_table(event_title, start_date, call_time, venue)
    return event_data

# Export data to CSV file
def write_csv():
    # Set up headers for the CSV file used to create the schedule and the table emailed to the team
    print("\nSetting up the CSV headers...\n")
    headers = ['start_date','subject', 'start_time', 'end_time', 'end_date', 'location', 'venue', 'description', 'description_1', 'merch_coordinator']

    # Generate calendar.csv in the ./csv_files folder that wil be used to create the schedule in a format that can be imported in Google Calendars
    print("Creating csv_files/calendar.csv...\n")
    with open('csv_files/calendar.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()

        for venue in venues_info:
            all_event_data = venues_info[venue]['event_info']
            for event_data in all_event_data:
                writer.writerow(event_data)
    print("Exported to " + os.getcwd() + "csv_files/calendar.csv\n")

# Build the email_data dictionary that will be emailed to the team
def create_email_table(event_title, start_date, call_time, venue):
    email_data = {
        'Artist': event_title,
        'Date': start_date.strftime('%Y-%m-%d'),
        'Call Time': call_time,
        'Venue': venue,
        }
    venues_info[venue]['email_data'].append(email_data)
    print(event_title, "||", start_date.strftime('%Y-%m-%d'), "||", call_time, "||", venue)
    return email_data

venues_info = {
    "EMO'S": {
        'url': "https://www.emosaustin.com/events-calendar",
        'location': "2015 E Riverside Dr, Austin, TX 78741",
        'event_info': [],
        'email_data': []
    },
    "SCOOT INN": {
        'url': "https://scootinnaustin.com/calendar",
        'location': "1308 E 4th St, Austin, TX 78702",
        'event_info': [],
        'email_data': []
    },
}

concurrent_shows = {
    "shows": []
}

# Compile all the event info
def compile_info():
    for venue, info in venues_info.items():
        print("\nGetting all the events from " + venue.title() + " for next month...\n")

        response = requests.get(info['url'])        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # # Uncomment the following lines to print the soup variable to txt files named after the corresponding 
            # # venue and see exactly what you are parsing. The files have been added to the .gitignore.
            # with open(f'txt_outputs/venue_data/{venue}_code.txt', 'w', encoding='utf-8') as python_output:
            #     sys.stdout = python_output
            #     print(soup)
            # sys.stdout = sys.__stdout__

            event_elements = soup.find_all('div', class_='frontgateFeedSummary')
            for event_element in event_elements:
                # Artist/Event name
                event_title = event_element.find('h2', class_='contentTitle').text.strip()                
                
                # Start date info
                month_element = event_element.find('span', class_='eventMonth').text.strip()
                day_element = event_element.find('span', class_='eventDay').text.strip()
                current_month = datetime.now().month
                year = datetime.now().year                
                if datetime.strptime(month_element, "%b").month < current_month:
                    year += 1
                else:
                    year = datetime.now().year
                month_numerical = datetime.strptime(month_element, "%b").month
                start_date_str = f"{year}-{month_numerical:02d}-{day_element}T00:00:00.000Z"
                start_date = datetime.strptime(start_date_str, "%Y-%m-%dT%H:%M:%S.%fZ").date()

                # Buy link (used in the event doors time not listed on venue event page)
                buy_button = event_element.find('a', class_='button buyButton')
                buy_link = buy_button['href']
                if "ticketmaster" in buy_link:
                    buy_link = buy_link.replace("www.ticketmaster.com", "concerts.livenation.com")
                
                # Doors time info (this logic is for the shows that display doors time on the event page)
                door_time = event_element.find('span', itemprop='doorTime')
                doors = door_time.text.strip() if door_time else ""
                doors_time_match = re.search(r'Doors open at\s+(\d{1,2}:\d{2}\s+[APap][Mm])', doors)
                doors_time_str = doors_time_match.group(1) if doors_time_match else "N/A"

                # Filter all the shows for next month
                filter_next_month(event_title, start_date, buy_link, doors_time_str, info['location'], venue)
        else:
            print("Failed to fetch the HTML content. Status code:", response.status_code)

# Search for doors time that are missing from event pages
def find_doors_time(tickets):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        "Cookie": f'{config["cookie"]}'
    }
    ticket_link = requests.get(tickets, headers=headers)        
    if ticket_link.status_code == 200:
        ticket_info = BeautifulSoup(ticket_link.content, 'html.parser')
        date_div = ticket_info.find('div', class_='event-header__event-date')
        if date_div == None:
            # This logic was created for www.zeffy.com
            description_tags = ticket_info.find_all('meta', attrs={'name': 'description'})
            doors_time_pattern = r'(\d{1,2}(:\d{2})?\s*[APap][Mm])'
            match = re.search(doors_time_pattern, description_tags[0]['content'])
            if match:
                time = match.group(1)
                time_obj = datetime.strptime(time, '%I%p')
                doors_time = time_obj.strftime('%I:%M %p')
                doors_time = doors_time.strip()
                return doors_time
            elif not match:
                # This logic was created for austin.rnbonly.com
                second_ticket_link = ticket_info.find('a', class_='button n01')
                browser = webdriver.Chrome()
                browser.get(second_ticket_link['href'])
                time_search = WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.XPATH, "//div[@class='event-item-single__time']")))
                search = time_search.text
                doors_time = search[0:7]
                doors_time.strip()
                browser.quit()
                return doors_time
            else:
                doors_time = '0:00 PM'
                print("Doors time not found. You'll need to inspect the code of the ticket info page, and add a condition specific to that page.")
                # print(tickets)
                return doors_time
        else:
            time_text = date_div.get_text()
            doors_time = time_text.split(' • ')[-1]
            doors_time = doors_time.strip()
            return doors_time

        # # The following will generate a file for each show with the data from the buy ticket page when uncommented.
        # # This will make the script execute a more slowly, but helpful if you need to look at the data you're parsing.
        #  with open(f'txt_outputs/{show}_code.txt', 'w', encoding='utf-8') as python_output:
        #     sys.stdout = python_output
        #     print(ticket_info)
        # sys.stdout = sys.__stdout__

# Format doors_time_str as datetime object and calculate call_time, end_time, and end_date
def format_times(start_date, doors_time_str, buy_link):
    if doors_time_str != "N/A":
        unformatted_doors_time = datetime.strptime(doors_time_str, "%I:%M %p")
    else:
        # Since doors_time N/A from event page, go to ticket info page
        doors_time = find_doors_time(buy_link)
        unformatted_doors_time = datetime.strptime(doors_time, "%I:%M %p")

    doors_time = unformatted_doors_time.strftime("%I:%M %p")
    unformatted_call_time = unformatted_doors_time - timedelta(hours=1)
    call_time = unformatted_call_time.strftime("%I:%M %p")
    end_dt = datetime.combine(start_date, unformatted_doors_time.time()).strftime('%Y-%m-%d %I:%M %p')
    end_datetime = (datetime.strptime(end_dt, '%Y-%m-%d %I:%M %p') + timedelta(hours=5)).strftime('%Y-%m-%d %I:%M %p')
    end_time = end_datetime[end_datetime.index(" "):].lstrip()
    end_date = end_datetime[0:end_datetime.index(" ")]
    # Format doors_time in HH:MM AM/PM format
    doors_time = unformatted_doors_time.strftime("%I:%M %p") if unformatted_doors_time else "N/A"

    return doors_time, call_time, end_time, end_date

# Filter on the shows for next month
def filter_next_month(event_title, start_date, buy_link, doors_time_str, location, venue):
    today = datetime.now()
    next_month_first_day = (today + timedelta(days=32)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_after_next_first_day = (today + timedelta(days=62)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    start_date = datetime.combine(start_date, datetime.min.time())

    # Find all the shows for next month and create the event_data tables
    if next_month_first_day <= start_date and start_date < month_after_next_first_day:
        # Convert doors_time_str to a datetime object and calculate call_time, end_time, and end_date
        doors_time, call_time, end_time, end_date = format_times(start_date, doors_time_str, buy_link)
        # Start putting all the event data together
        create_event_data(event_title, start_date, call_time, doors_time, end_date, end_time, location, venue)

# Start compiling the show details
compile_info()

# Find dates when there are concurrent shows at venues
def find_concurrent_shows(*args):
    for arg in args:
        emos_dates = set(data['start_date'] for data in venues_info["EMO'S"]['event_info'])
        scoot_inn_dates = set(data['start_date'] for data in venues_info["SCOOT INN"]['event_info'])

    common_dates = emos_dates.intersection(scoot_inn_dates)
    concurrent_dates.append(common_dates)
    print("\nThe following dates have shows at all venues:", common_dates ,'\n')

    print("Those corresponding shows are:\n")
    for date in common_dates:
        for venue in venues_info:
            number_of_events = len(venues_info[venue]['event_info'])
            
            for i in range(number_of_events):
                event_info = venues_info[venue]['event_info'][i]
                venue_start_date = event_info['start_date']
                event_name = event_info['subject']
                event_start_time = event_info['start_time']
                if venue_start_date == date:
                    same_shows = [event_name, venue_start_date, event_start_time, venue]
                    concurrent_shows['shows'].append(same_shows)
                    print(event_name, "||", venue_start_date, "||", event_start_time, "||", venue)

# Find concurrent shows
find_concurrent_shows(venues_info["EMO'S"]['event_info'], venues_info["SCOOT INN"]['event_info'])

# Write the CSV
write_csv()
