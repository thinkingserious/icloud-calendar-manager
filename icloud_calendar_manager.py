import os
import caldav
from caldav.elements import dav, cdav
import datetime
import requests
import json
import logging
from typing import Dict, List, Optional
from requests.auth import HTTPBasicAuth

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('icloud_caldav.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

APPLE_ID = os.getenv('APPLE_ID')
APPLE_PASSWORD = os.getenv('APPLE_PASSWORD')
CALENDAR_URL_FILE = 'caldav_endpoint.json'


def validate_env_variables():
    """Validate that essential environment variables are set."""
    if not APPLE_ID or not APPLE_PASSWORD:
        logger.error("APPLE_ID or APPLE_PASSWORD environment variables are not set.")
        raise EnvironmentError("Missing required environment variables.")


validate_env_variables()


def authenticate_and_build_url() -> Optional[str]:
    """
    Authenticate to iCloud and construct the CalDAV base URL.

    Returns:
        The CalDAV full URL or None if authentication fails.
    """
    try:
        auth_data = authenticate_icloud(APPLE_ID, APPLE_PASSWORD)
        if not auth_data:
            logger.error("Authentication failed. Cannot proceed.")
            return None

        return build_caldav_endpoint(auth_data, CALENDAR_URL_FILE)
    except Exception as e:
        logger.error(f"Failed to authenticate and build URL: {e}")
        return None


def authenticate_icloud(username: str, app_password: str) -> Optional[Dict[str, str]]:
    """
    Authenticate to iCloud using the provided credentials.

    Args:
        username: Apple ID username.
        app_password: App-specific password.

    Returns:
        A dictionary containing authentication data or None if authentication fails.
    """
    try:
        auth_url = 'https://setup.icloud.com/setup/ws/1/login'
        payload = {'apple_id': username, 'password': app_password}
        session = requests.Session()
        session.auth = HTTPBasicAuth(username, app_password)
        session.headers.update({'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'})

        response = session.post(auth_url, json=payload)
        response.raise_for_status()
        auth_data = response.json()

        logger.info("Authentication successful.")
        return {
            'session': session,
            'dsid': auth_data.get('dsid'),
            'p_value': auth_data.get('p')
        }
    except requests.RequestException as e:
        logger.error(f"Authentication error: {e}")
        return None


def build_caldav_endpoint(auth_info: Dict[str, str], output_file: str) -> Optional[str]:
    """
    Build the CalDAV endpoint URL and save it to a file.

    Args:
        auth_info: Authentication information containing p_value and dsid.
        output_file: The file to save the CalDAV URL.

    Returns:
        The full CalDAV URL or None if an error occurs.
    """
    try:
        if 'p_value' not in auth_info or 'dsid' not in auth_info:
            logger.error("Invalid authentication data.")
            return None

        caldav_base_url = f'https://p{auth_info["p_value"]}-caldav.icloud.com'
        dsid = auth_info['dsid']
        endpoint_config = {
            'base_url': caldav_base_url,
            'dsid': dsid,
            'full_url': f'{caldav_base_url}/{dsid}/calendars/'
        }

        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(endpoint_config, f, indent=4)

        logger.info(f"CalDAV endpoint saved to {output_file}.")
        return endpoint_config['full_url']
    except Exception as e:
        logger.error(f"Error building CalDAV endpoint: {e}")
        return None


def get_caldav_client(base_url: Optional[str] = None) -> Optional[caldav.DAVClient]:
    """
    Get a CalDAV client for interacting with the server.

    Args:
        base_url: Optional base URL to use; otherwise, it reads from the file.

    Returns:
        A DAVClient instance or None if an error occurs.
    """
    try:
        if not base_url:
            base_url = read_caldav_url_from_file(CALENDAR_URL_FILE)

        if not base_url:
            logger.info("URL missing or invalid. Rebuilding...")
            base_url = authenticate_and_build_url()

        if not base_url:
            logger.error("Failed to retrieve or rebuild the CalDAV URL.")
            return None

        return caldav.DAVClient(url=base_url, username=APPLE_ID, password=APPLE_PASSWORD)
    except Exception as e:
        logger.error(f"Error creating CalDAV client: {e}")
        return None


def read_caldav_url_from_file(file_path: str) -> Optional[str]:
    """
    Read the CalDAV URL from a file.

    Args:
        file_path: The file containing the CalDAV URL.

    Returns:
        The CalDAV URL or None if an error occurs.
    """
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = json.load(f)
                return data.get('full_url')
        else:
            logger.warning(f"File {file_path} does not exist.")
            return None
    except Exception as e:
        logger.error(f"Error reading CalDAV URL from file: {e}")
        return None


def safe_request(func):
    """
    Decorator to safely handle network requests with retries.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.RequestException as e:
            logger.error(f"Network error: {e}")
            return None
    return wrapper


def find_calendar(principal, calendar_name: str) -> Optional[caldav.objects.Calendar]:
    """
    Helper function to find a specific calendar by name.

    Args:
        principal: The CalDAV principal object.
        calendar_name: The name of the calendar to find.

    Returns:
        The Calendar object or None if not found.
    """
    calendars = principal.calendars()
    return next((cal for cal in calendars if cal.name == calendar_name), None)


@safe_request
def discover_caldav_calendars() -> Optional[List[caldav.objects.Calendar]]:
    """
    Discover all available calendars for the authenticated user.

    Returns:
        A list of Calendar objects or None if an error occurs.
    """
    try:
        client = get_caldav_client()
        if not client:
            return None

        principal = client.principal()
        calendars = principal.calendars()

        if calendars:
            logger.info("Calendars discovered:")
            for cal in calendars:
                logger.info(f"- {cal.name} ({cal.url})")
        else:
            logger.info("No calendars found.")
        return calendars

    except caldav.lib.error.AuthorizationError as e:
        logger.error(f"Authorization error: {e}")
        return None
    except Exception as e:
        logger.error(f"Error discovering calendars: {e}")
        return None


@safe_request
def get_apple_calendar_events(calendar_name: str, start_date: datetime.datetime, end_date: datetime.datetime) -> Optional[List]:
    """
    Retrieve events from a specific calendar within a date range.

    Args:
        calendar_name: The name of the calendar.
        start_date: The start date for the event search.
        end_date: The end date for the event search.

    Returns:
        A list of events or None if an error occurs.
    """
    try:
        client = get_caldav_client()
        if not client:
            return None

        principal = client.principal()
        calendar = find_calendar(principal, calendar_name)

        if calendar:
            events = calendar.date_search(start=start_date, end=end_date)
            return events
        else:
            logger.error(f"Calendar '{calendar_name}' not found.")
            return None
    except Exception as e:
        logger.error(f"Error retrieving events: {e}")
        return None


@safe_request
def add_event_to_calendar(calendar_name: str, summary: str, start_time: datetime.datetime, end_time: datetime.datetime) -> bool:
    """
    Add an event to a specific calendar.

    Args:
        calendar_name: The name of the calendar.
        summary: The summary of the event.
        start_time: The start time of the event.
        end_time: The end time of the event.

    Returns:
        True if the event was added successfully, False otherwise.
    """
    try:
        client = get_caldav_client()
        if not client:
            return False

        principal = client.principal()
        calendar = find_calendar(principal, calendar_name)

        if calendar:
            calendar.save_event(
                dtstart=start_time,
                dtend=end_time,
                summary=summary
            )
            return True
        else:
            logger.error(f"Calendar '{calendar_name}' not found.")
            return False
    except Exception as e:
        logger.error(f"Error adding event: {e}")
        return False


@safe_request
def update_event_in_calendar(calendar_name: str, event_uid: str, summary: str, start_time: datetime.datetime, end_time: datetime.datetime) -> bool:
    """
    Update an event in a specific calendar.

    Args:
        calendar_name: The name of the calendar.
        event_uid: The UID of the event to update.
        summary: The new summary of the event.
        start_time: The new start time of the event.
        end_time: The new end time of the event.

    Returns:
        True if the event was updated successfully, False otherwise.
    """
    try:
        client = get_caldav_client()
        if not client:
            return False

        principal = client.principal()
        calendar = find_calendar(principal, calendar_name)

        if calendar:
            event = calendar.event(event_uid)
            event.load()
            event.instance.vevent.summary.value = summary
            event.instance.vevent.dtstart.value = start_time
            event.instance.vevent.dtend.value = end_time
            event.save()
            return True
        else:
            logger.error(f"Calendar '{calendar_name}' not found.")
            return False
    except Exception as e:
        logger.error(f"Error updating event: {e}")
        return False


@safe_request
def delete_event_from_calendar(calendar_name: str, event_uid: str) -> bool:
    """
    Delete an event from a specific calendar.

    Args:
        calendar_name: The name of the calendar.
        event_uid: The UID of the event to delete.

    Returns:
        True if the event was deleted successfully, False otherwise.
    """
    try:
        client = get_caldav_client()
        if not client:
            return False

        principal = client.principal()
        calendar = find_calendar(principal, calendar_name)

        if calendar:
            event = calendar.event(event_uid)
            event.delete()
            return True
        else:
            logger.error(f"Calendar '{calendar_name}' not found.")
            return False
    except Exception as e:
        logger.error(f"Error deleting event: {e}")
        return False


@safe_request
def list_calendars() -> Optional[List[Dict[str, str]]]:
    """
    List all available calendars.

    Returns:
        A list of dictionaries containing calendar names and URLs, or None if an error occurs.
    """
    try:
        client = get_caldav_client()
        if not client:
            return None

        principal = client.principal()
        calendars = principal.calendars()

        return [{'name': cal.name, 'url': cal.url} for cal in calendars]
    except Exception as e:
        logger.error(f"Error listing calendars: {e}")
        return None


# Example usage
if __name__ == "__main__":
    caldav_url = discover_caldav_calendars()
    if caldav_url:
        logger.info("Successfully accessed iCloud calendars.")

        # List calendars
        calendars = list_calendars()
        if calendars:
            logger.info("\nCalendars:")
            for cal in calendars:
                logger.info(f"- {cal['name']} ({cal['url']})")

        # Example: Get events for a specific calendar
        calendar_name = "calendar_name"
        start_date = datetime.datetime.now()
        end_date = start_date + datetime.timedelta(days=7)
        events = get_apple_calendar_events(calendar_name, start_date, end_date)
        if events:
            logger.info(f"\nEvents in '{calendar_name}' for the next 7 days:")
            for event in events:
                logger.info(f"- {event.instance.vevent.summary.value}")

        # Example: Add an event
        add_event_to_calendar(calendar_name, "[Testing] New Event", start_date, end_date)

        # Note: For update and delete operations, you'd need the event's UID,
        # which you can get from the event objects returned by get_apple_calendar_events
    else:
        logger.error("Failed to access iCloud CalDAV.")
