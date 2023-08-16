import requests, re, sys, os, json, csv, time
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

config = json.load(open("config_files/parameters.json"))

def create_event_data(event_title, start_date, call_time, doors_time, end_date, end_time, location, venue):
    # Build the event_data dictionary that will populate venues_info["EMO'S"]['event_info']
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

    # create the email_tables
    create_email_table(event_title, start_date, call_time, venue)
    return event_data

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
            # Iterate through the data and write each row to the CSV
            for event_data in all_event_data:
                writer.writerow(event_data)
    print("Exported to " + os.getcwd() + "csv_files/calendar.csv\n")

def create_email_table(event_title, start_date, call_time, venue):
    # Build the email_data dictionary that will be emailed to the team
    email_data = {
        'Artist': event_title,
        'Date': start_date.strftime('%Y-%m-%d'),
        'Call Time': call_time,
        'Venue': venue,
        }
    print(event_title, "||", start_date.strftime('%Y-%m-%d'), "||", call_time, "||", venue)
    return email_data

venues_info = {
    "EMO'S": {
        'url': "https://www.emosaustin.com/events-calendar",
        'location': "2015 E Riverside Dr, Austin, TX 78741",
        'event_info': [],
    },
    "SCOOT INN": {
        'url': "https://scootinnaustin.com/calendar",
        'location': "1308 E 4th St, Austin, TX 78702",
        'event_info': [],
    },
}

def compile_info():
    for venue, info in venues_info.items():
        print("\nGetting all the events from " + venue.title() + " for next month.\n")

        response = requests.get(info['url'])        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # # Uncomment the following lines to print the soup variable to txt files named after the corresponding 
            # # venue and see exactly what you are parsing. The files have been added to the .gitignore.
            # with open(f'txt_outputs/venue_data/{venue}_code.txt', 'w', encoding='utf-8') as python_output:
            #     sys.stdout = python_output
            #     print(soup)
            # sys.stdout = sys.__stdout__

            # Find all elements with class="frontgateFeedSummary"
            event_elements = soup.find_all('div', class_='frontgateFeedSummary')
            # Iterate through each event element and extract relevant data
            for event_element in event_elements:
                # Extract event details
                event_title = event_element.find('h2', class_='contentTitle').text.strip()                
                # Extract event dates and set some default values for calculation
                month_element = event_element.find('span', class_='eventMonth').text.strip()
                day_element = event_element.find('span', class_='eventDay').text.strip()
                current_month = datetime.now().month
                year = datetime.now().year                
                buy_button = event_element.find('a', class_='button buyButton')
                buy_link = buy_button['href']

                # Update ticket page to the redirect
                if "ticketmaster" in buy_link:
                    buy_link = buy_link.replace("www.ticketmaster.com", "concerts.livenation.com")
                
                # Establish the year and build the date variable
                if datetime.strptime(month_element, "%b").month < current_month:
                    year += 1
                else:
                    year = datetime.now().year

                month_numerical = datetime.strptime(month_element, "%b").month
                start_date_str = f"{year}-{month_numerical:02d}-{day_element}T00:00:00.000Z"
                start_date = datetime.strptime(start_date_str, "%Y-%m-%dT%H:%M:%S.%fZ").date()
                door_time = event_element.find('span', itemprop='doorTime')
                doors = door_time.text.strip() if door_time else ""
                doors_time_match = re.search(r'Doors open at\s+(\d{1,2}:\d{2}\s+[APap][Mm])', doors)
                doors_time_str = doors_time_match.group(1) if doors_time_match else "N/A"

                unformatted_doors_time = None
                doors_time = None
                unformatted_call_time = None
                call_time = None
                end_time = None
                end_date = None
                
                # Convert doors_time_str to a datetime object
                if doors_time_str != "N/A":
                    unformatted_doors_time = datetime.strptime(doors_time_str, "%I:%M %p")
                    doors_time = unformatted_doors_time.strftime("%I:%M %p")
                    unformatted_call_time = unformatted_doors_time - timedelta(hours=1)
                    call_time = unformatted_call_time.strftime("%I:%M %p")
                    end_dt = datetime.combine(start_date, unformatted_doors_time.time()).strftime('%Y-%m-%d %I:%M %p')
                    end_datetime = (datetime.strptime(end_dt, '%Y-%m-%d %I:%M %p') + timedelta(hours=5)).strftime('%Y-%m-%d %I:%M %p')
                    end_time = end_datetime[end_datetime.index(" "):].lstrip()
                    end_date = end_datetime[0:end_datetime.index(" ")]                
                else:
                    doors_time = find_doors_time(buy_link, event_title)
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

                # Filter all the shows for next month
                filter_next_month(event_title, start_date, call_time, doors_time, end_date, end_time, info['location'], venue)
        else:
            print("Failed to fetch the HTML content. Status code:", response.status_code)

# Create a function to fill in missing door times
def find_doors_time(tickets, show):
    # Define the request headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        "Cookie": f'{config["cookie"]}'
    }
    # Fetch the HTML content using requests
    ticket_link = requests.get(tickets, headers=headers)        
    # Check if the request was successful
    if ticket_link.status_code == 200:
        # Parse the HTML using BeautifulSoup
        ticket_info = BeautifulSoup(ticket_link.content, 'html.parser')
        # Find the div with class "event-header__event-date" and get its text
        date_div = ticket_info.find('div', class_='event-header__event-date')
        # print(date_div)
        if date_div == None:
            description_tags = ticket_info.find_all('meta', attrs={'name': 'description'})
            # Define the regular expression pattern to extract the doors time
            doors_time_pattern = r'(\d{1,2}(:\d{2})?\s*[APap][Mm])'
            # Search for the pattern in the HTML code
            match = re.search(doors_time_pattern, description_tags[0]['content'])
            # Check if a match was found
            if match:
                # Extract the doors time from the matched text
                time = match.group(1)
                # Parse the input string into a datetime object
                time_obj = datetime.strptime(time, '%I%p')
                # Format the datetime object as '%I:%M %p'
                doors_time = time_obj.strftime('%I:%M %p')
                doors_time = doors_time.strip()
                return doors_time
            elif not match:
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
                doors_time = 000000
                print("Doors time not found. You'll need to inspect the code of the ticket info page, and add a condition specific to that page.")
                # print(tickets)
                return doors_time
        else:
            # Extract the time from the text (assuming the time format is consistent)
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

# Filter on the shows for next month
def filter_next_month(event_title, start_date, call_time, doors_time, end_date, end_time, location, venue):
    # Get the first day of next month and the month after to set our limits
    today = datetime.now()
    next_month_first_day = (today + timedelta(days=32)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_after_next_first_day = (today + timedelta(days=62)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    start_date = datetime.combine(start_date, datetime.min.time())

    # Find all the shows for next month and create the event_data tables
    if next_month_first_day <= start_date and start_date < month_after_next_first_day:
        create_event_data(event_title, start_date, call_time, doors_time, end_date, end_time, location, venue)

compile_info() # start compiling the show details

# Find dates when there are concurrent shows at venues
def find_concurrent_shows(*args):
    # Extract the dates from the venues
    for arg in args:
        emos_dates = set(data['start_date'] for data in venues_info["EMO'S"]['event_info'])
        scoot_inn_dates = set(data['start_date'] for data in venues_info["SCOOT INN"]['event_info'])

    # Find the common dates where both venues have events
    common_dates = emos_dates.intersection(scoot_inn_dates)
    print("\nThe following dates have shows at all venues:", common_dates ,'\n')
    # for date in common_dates:
    #     print(date)

    print("Those corresponding shows are:\n")
    # Compare both lists to identify which shows occur on the same day
    for date in common_dates:
        for venue in venues_info:
            number_of_events = len(venues_info[venue]['event_info'])
            
            for i in range(number_of_events):
                event_info = venues_info[venue]['event_info'][i]
                venue_start_date = event_info['start_date']
                event_name = event_info['subject']
                event_start_time = event_info['start_time']
                if venue_start_date == date:
                    # Print the common dates and associated info
                    print(event_name, "||", venue_start_date, "||", event_start_time, "||", venue)

find_concurrent_shows(venues_info["EMO'S"]['event_info'], venues_info["SCOOT INN"]['event_info'])

# Write the CSV
write_csv()