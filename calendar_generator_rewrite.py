import requests, re, sys
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def create_event_data(event_title, start_date, call_time, doors_time, end_date, end_time, location, venue):
    i = 0
    event_data = {
        'subject': event_title,
        'start_date': start_date,
        'start_time': call_time,
        'end_time': end_time,
        'end_date': end_date,
        'location': location,
        'venue': venue,
        'description': f"=CONCATENATE(H{i + 2},UPPER(I{i + 2}))",
        'description_1': f"DOORS TIME: {doors_time}\n VENUE: {venue}\n MERCH COORDINATOR:"
    }
    venues_info[venue]['event_info'].append(event_data)
    # print(event_data)
    i += 1
    # create the email_tables
    create_email_table(event_title, start_date, call_time, venue)
    return event_data

def create_email_table(event_title, start_date, call_time, venue):
    email_data = {
        'Artist': event_title,
        'Date': start_date,
        'Call Time': call_time,
        'Venue': venue,
        }
    print(email_data)
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

        # Fetch the HTML content using requests
        response = requests.get(info['url'])        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML using BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')

            # Uncomment the following lines to print the soup variable to txt files named after the corresponding 
            # venue and see exactly what you are parsing. The files have been added to the .gitignore.
            
            # with open(f'{venue}.txt', 'w', encoding='utf-8') as python_output:
            #     # Redirect the standard output to the file
            #     sys.stdout = python_output
            #     print(soup)
            # # Restore the default standard output
            # sys.stdout = sys.__stdout__

            # Find all elements with class="frontgateFeedSummary"
            event_elements = soup.find_all('div', class_='frontgateFeedSummary')
            # Iterate through each event element and extract relevant data
            for event_element in event_elements:
                # Extract event details
                event_title = event_element.find('h2', class_='contentTitle').text.strip()
                # Extract event dates
                month_element = event_element.find('span', class_='eventMonth').text.strip()
                day_element = event_element.find('span', class_='eventDay').text.strip()
                current_month = datetime.now().month
                # Establish the year and build the date variable
                if datetime.strptime(month_element, "%b").month < current_month:
                    year += 1
                else:
                    year = datetime.now().year

                month_numerical = datetime.strptime(month_element, "%b").month
                start_date = f"{year}-{month_numerical:02d}-{day_element}T00:00:00.000Z"
                year = datetime.now().year
                start_date = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S.%fZ")
                
                # Extract event description and handle nonexisting elements
                door_time = event_element.find('span', itemprop='doorTime')
                doors = door_time.text.strip() if door_time else ""
                # Extract doors time from event description using regular expressions
                doors_time_match = re.search(r'Doors open at\s+(\d{1,2}:\d{2}\s+[APap][Mm])', doors)
                doors_time_str = doors_time_match.group(1) if doors_time_match else "N/A"

                unformatted_doors_time = None
                doors_time = "N/A"
                unformatted_call_time = None
                call_time = "N/A"
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

                # Format doors_time in HH:MM AM/PM format
                doors_time = unformatted_doors_time.strftime("%I:%M %p") if unformatted_doors_time else "N/A"

                # Filter all the shows for next month
                filter_next_month(event_title, start_date, call_time, doors_time, end_date, end_time, info['location'], venue)
        else:
            print("Failed to fetch the HTML content. Status code:", response.status_code)

# Filter on the shows for next month
def filter_next_month(event_title, start_date, call_time, doors_time, end_date, end_time, location, venue):
    # Get the first day of next month and the month after
    today = datetime.now()
    next_month_first_day = (today + timedelta(days=32)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_after_next_first_day = (today + timedelta(days=62)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    start_date = datetime.combine(start_date, datetime.min.time())

    # Find all the shows for next month and create the event_data tables
    if next_month_first_day <= start_date and start_date < month_after_next_first_day:
        create_event_data(event_title, start_date, call_time, doors_time, end_date, end_time, location, venue)

compile_info()

# Find dates when there are concurrent shows at venues
def find_concurrent_shows(*args):
    # Extract the dates from the venues
    for arg in args:
        # print(arg[0])
        emos_dates = set(data['start_date'] for data in venues_info["EMO'S"]['event_info'])
        scoot_inn_dates = set(data['start_date'] for data in venues_info["SCOOT INN"]['event_info'])

    print("\nThe following dates have shows at all venues:")
    # Find the common dates where both venues have events
    common_dates = emos_dates.intersection(scoot_inn_dates)
    print(common_dates, '\n')

    print("Those shows are as follows:\n")

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
                    print(event_name, date, event_start_time, venue)

find_concurrent_shows(venues_info["EMO'S"]['event_info'], venues_info["SCOOT INN"]['event_info'])