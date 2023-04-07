
import datetime
import os.path
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build

# Define file paths
CREDENTIALS_FILE = 'client_secret.json'
TOKEN_FILE = 'token.pickle'
INPUT_FILE = 'input.txt'
OUTPUT_FILE = 'output.txt'

# Define API scopes and version
API_SERVICE_NAME = 'calendar'
API_VERSION = 'v3'
API_SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def authenticate():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, API_SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    return creds
def get_events(start_date, end_date):
    creds = authenticate()
    service = build(API_SERVICE_NAME, API_VERSION, credentials=creds)
    events_result = None
    try:
        events_result = service.events().list(
            calendarId='primary',
            timeMin=start_date.isoformat() + 'Z',
            timeMax=end_date.isoformat() + 'Z',
            maxResults=1000,
            singleEvents=True,
            orderBy='startTime',
            fields='items(summary,location,start,end,attendees,colorId)'
        ).execute()
    except HttpError as error:
        print(f'An error occurred: {error}')
    events = events_result.get('items', [])
    return events

def read_dates():
    with open(INPUT_FILE, 'r') as f:
        start_date, end_date = f.readline().split(',')
        start_date = datetime.datetime.strptime(start_date.strip(), '%Y-%m-%d')
        end_date = datetime.datetime.strptime(end_date.strip(), '%Y-%m-%d')
    return start_date, end_date

def write_events(events):
    with open(OUTPUT_FILE, 'w') as f:
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            summary = event['summary']
            location = event.get('location', 'No location provided')
            attendees = event.get('attendees', [])
            attendee_emails = [attendee['email'] for attendee in attendees]
            color_id = event.get('colorId', 'No color ID provided')
            f.write(f'{start} to {end} - {summary}\n')
            f.write(f'Location: {location}\n')
            f.write(f'Attendees: {attendee_emails}\n')
            f.write(f'Color ID: {color_id}\n\n')

def main():
    start_date, end_date = read_dates()
    events = get_events(start_date, end_date)
    if events:
        write_events(events)
    else:
        print('No events found.')

if __name__ == '__main__':
    main()

