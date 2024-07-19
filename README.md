# iCloud Calendar Manager

This script provides a simple interface to interact with iCloud calendars using the CalDAV protocol.

## Requirements

- Python 3.6+
- `caldav` library

## Setup

1. Clone this repository or download the script.

2. Install the required library:

```bash
pip install -r requirements.txt
```

3. Set up environment variables:

- On Unix-based systems (Linux, macOS):

```bash
export APPLE_ID='your_apple_id@example.com'
export APPLE_PASSWORD='your_app_specific_password'
```

- On Windows:

```bash
set APPLE_ID=your_apple_id@example.com
set APPLE_PASSWORD=your_app_specific_password
```

Note: Replace 'your_apple_id@example.com' with your actual Apple ID, and 'your_app_specific_password' with an app-specific password.

4. Creating an App-Specific Password:

- Go to https://appleid.apple.com/ and sign in.
- In the Security section, click "Generate Password" under App-Specific Passwords.
- Follow the steps to create a password and use this as your APPLE_PASSWORD.

## Running in GitHub Codespaces

### Using the Terminal

1. **Fork the Repository:**

   - Navigate to the repository on GitHub.
   - Click the `Fork` button at the top right corner to create your own copy of the repository.

2. **Create a Codespace:**

   - Navigate to your forked repository on GitHub.
   - Click the `Code` button.
   - Select the `Codespaces` tab.
   - Click `New codespace` to create a new Codespace.

3. **Set up Environment Variables:**

   - Once the Codespace is running, open the terminal.
   - Set up the environment variables:

     ```bash
     echo 'export APPLE_ID="your_apple_id@example.com"' >> ~/.bashrc
     echo 'export APPLE_PASSWORD="your_app_specific_password"' >> ~/.bashrc
     source ~/.bashrc
     ```

4. **Install Required Libraries:**

   - In the terminal, run:

     ```bash
     pip install -r requirements.txt
     ```

5. **Modify the Script:**

   - In the Codespace file explorer, open the script file (`icloud_calendar_manager.py`).
   - Modify the `calendar_name` variable in the `if __name__ == "__main__":` block to match one of your iCloud calendar names.

6. **Run the Script:**

   - In the terminal, run:

     ```bash
     python icloud_calendar_manager.py
     ```

### Using the UI

1. **Fork the Repository:**

   - Navigate to the repository on GitHub.
   - Click the `Fork` button at the top right corner to create your own copy of the repository.

2. **Create a Codespace:**

   - Navigate to your forked repository on GitHub.
   - Click the `Code` button.
   - Select the `Codespaces` tab.
   - Click `New codespace` to create a new Codespace.

3. **Add Secrets in Repository Settings:**

   - Navigate to your forked repository on GitHub.
   - Go to `Settings` > `Secrets and variables` > `Codespaces`.
   - Click `New repository secret`.
   - Add the following secrets:

     - `APPLE_ID`: your_apple_id@example.com
     - `APPLE_PASSWORD`: your_app_specific_password

4. **Access Secrets in Codespace:**

   - Once the Codespace is running, the secrets will be available as environment variables.

5. **Install Required Libraries:**

   - Open a terminal in the Codespace.
   - Run the following command:

     ```bash
     pip install -r requirements.txt
     ```

6. **Modify the Script:**

   - In the Codespace file explorer, open the script file (`icloud_calendar_manager.py`).
   - Modify the `calendar_name` variable in the `if __name__ == "__main__":` block to match one of your iCloud calendar names.

7. **Run the Script:**

   - In the terminal, run:

     ```bash
     python icloud_calendar_manager.py
     ```

## Usage

1. Open the script and modify the `calendar_name` variable in the `if __name__ == "__main__":` block to match one of your iCloud calendar names.

2. Run the script:

```bash
python icloud_calendar_manager.py
```

3. The script will:

- List all available calendars
- Show events for the specified calendar for the next 7 days
- Add a sample event to the specified calendar

## Functions

- `discover_caldav_calendars()`: Lists all available calendars.
- `get_apple_calendar_events(calendar_name, start_date, end_date)`: Retrieves events for a specific calendar within a date range.
- `add_event_to_calendar(calendar_name, summary, start_time, end_time)`: Adds a new event to a calendar.
- `update_event_in_calendar(calendar_name, event_uid, summary, start_time, end_time)`: Updates an existing event.
- `delete_event_from_calendar(calendar_name, event_uid)`: Deletes an event from a calendar.
- `list_calendars()`: Returns a list of all calendars.

## Notes

- This script uses the CalDAV protocol to interact with iCloud calendars. Make sure your iCloud account has CalDAV access enabled.
- Always keep your Apple ID and app-specific password secure. Never share them or commit them to version control.
- If you encounter authentication issues, ensure you're using an app-specific password and that your Apple ID doesn't have any restrictions preventing third-party access.

## Troubleshooting

If you encounter issues:

1. Verify your Apple ID and app-specific password are correct.
2. Ensure two-factor authentication is properly handled (use an app-specific password).
3. Check if there are any restrictions on your Apple ID preventing third-party access.
4. If problems persist, you may need to contact Apple Support for further assistance with accessing CalDAV services for your account.
