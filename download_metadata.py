import functools
import json
import os
import sys
import threading
import time
import uuid
import webbrowser
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Optional, Dict, List, Literal, Tuple, Any

import msal
import requests
import urllib3

# @see v1 Claude AI prompting to create the below code [https://claude.ai/chat/80e54656-3b6f-409b-8bb8-294440e22c21]
# @see v2 Claude AI promtping [https://claude.ai/chat/a5219819-b864-406e-a15c-d7e0b5402025]

# CHANGE THESE TO YOUR AZURE APPLICATION:
# See "Setting up client_id, client_secret & tenant_id:" below for instructions on how to setup <client_id> / <client_secret>
# e...v@gmail.com
CLIENT_ID = "<YOUR CLIENT_ID>",
CLIENT_SECRET = "<YOUR CLIENT_SECRET>"

"""

INITIAL PROMPT:

Hello, act as my software engineering computer science graduate.

I have a Python app that lists files in OneDrive...

# V3 ONEDRIVE FILE LISTER WITH METADATA

Hi Claude! I need you to help me maintain and enhance this code. Let me explain what we've built and what you need to know:

### What This App Does

I built this to get a complete inventory of OneDrive and SharePoint files with metadata for auditing and tracking. It:
* Lists all files/folders recursively from OneDrive personal/business accounts
* Lists all SharePoint sites, their document libraries, and recycling bins
* Outputs detailed metadata in tab-separated format for spreadsheet analysis
* Runs unattended after initial authentication
* Handles large file systems (100,000+ files) reliably

### Key Architectural Points

* Uses Microsoft Graph API via MSAL authentication
* Separates data (stdout) from diagnostic logging (stderr)
* Two main recursion functions:
 - list_files_recursively (OneDrive)
 - process_sharepoint_folder (SharePoint libraries)
  All file/folder operations go through OneDriveUserClient class

### Technical Solutions to Non-Obvious Problems

* Token refresh: Silent refresh every 20 mins, fallback to interactive
* Network resilience: Exponential backoff with 20 retries up to 15 min delays
* Path encoding: URL-safe encoding of special characters in paths
* Auth cleanup: Proper token/session cleanup even on crashes
* Error handling: Only retry appropriate errors (not 404s), graceful degradation
* Idempotency: Remove downloadUrls from metadata, maintain deterministic output

### Engineering Principles to Remember

1. Keep diagnostic logging separate from data output
2. Handle network/auth issues gracefully - these are long-running processes
3. Make output idempotent where possible for comparison
4. Fail gracefully and clean up properly
5. Don't retry permanent errors (like 404s)

Remember: Clean, focused code that does one thing well is better than clever, complex code doing many things.

The retry stuff and token handling are super important since this can run for hours crawling through large OneDrives.

I can show you the code next - it's really well done and includes solid error handling. Want me to paste it in?

----

SECOND PROMPT

OK here is the code - explain back to me what it does:
```
...
```
"""

"""
Setting up client_id, client_secret & tenant_id:

Let's walk through creating a new app registration in Azure Portal:

Go to Azure Portal (https://portal.azure.com)
Search for and select "Azure Active Directory" (or "Microsoft Entra ID" in newer portals)
Click on "App registrations" in the left menu
Click "+ New registration" at the top

Name: "OneDriveAutomation" (or your preferred name)
Supported account types: Choose "Accounts in any organizational directory (Any Azure AD directory - Multitenant) and personal Microsoft accounts (e.g. Skype, Xbox)"
Redirect URI: Select "Web" and enter "http://localhost:8000"
Click "Register"

On the next screen, note down:

Application (client) ID - this is your client_id
Directory (tenant) ID - this is your tenant_id

To create a client_secret:

Click "Certificates & secrets" in the left menu
Under "Client secrets", click "+ New client secret"
Add a description (e.g., "OneDrive Access")
Choose an expiration
Click "Add"
IMMEDIATELY copy the generated secret value - this is your client_secret

Configure API permissions:

Click "API permissions" in the left menu
Click "Add a permission"
Choose "Microsoft Graph"
Choose "Delegated permissions"

Search for and select:

Files.Read
Files.Read.All
Files.ReadWrite
Files.ReadWrite.All
User.Read

Click "Add permissions"
Click "Grant admin consent" button at top

The key part is selecting the correct "Supported account types" in step 4 - it needs to include personal Microsoft accounts since that's what's causing your error.
"""

"""
Running:
python3 main.py 2>&1 | tee output.txt

Example Use:

# List files in root directory
files = client.list_files()
for file in files:
    print(f"Name: {file['name']}, Type: {file.get('file') and 'File' or 'Folder'}")

# List and display files with details
root_files = client.list_files()  # Root directory

print("\nFiles in Root Directory:")
print("=" * 80)
print(f"{'Name':<40} {'Type':<10} {'Last Modified'}")
print("-" * 80)

for file in root_files:
    # Get file name
    name = file.get('name', 'Unknown')

    # Determine type (Folder or File)
    file_type = 'Folder' if 'folder' in file else 'File'

    # Get last modified date and format it
    modified = file.get('lastModifiedDateTime', 'Unknown')
    # Optionally format the date to be more readable
    if modified != 'Unknown':
        # Convert from ISO format to more readable format
        try:
            from datetime import datetime

            modified_date = datetime.strptime(modified, "%Y-%m-%dT%H:%M:%SZ")
            modified = modified_date.strftime("%Y-%m-%d %H:%M")
        except:
            pass

    print(f"{name:<40} {file_type:<10} {modified}")

print("=" * 80)

# Rest of the examples...
doc_files = client.list_files("Documents")  # Documents folder
subfolder_files = client.list_files("Documents/Reports")  # Nested folder

# Upload a file
client.upload_file(
    file_path="local_document.docx",
    destination_path="Documents"  # The OneDrive folder to upload to
)

# Download a file
client.download_file(
    file_path="Documents/report.pdf",  # Path in OneDrive
    local_path="downloaded_report.pdf"  # Where to save locally
)

# Create a new folder
client.create_folder("Documents/NewProject2024")

# Get a sharing link for a file
share_link = client.get_sharing_link(
    file_path="Documents/report.pdf",
    type="view"  # or "edit" for edit permissions
)

# Delete a file
client.delete_file("Documents/old_file.txt")

# Check who you're authenticated as
current_user = client.get_current_user()
print(f"\nCurrently logged in as: {current_user}")

# Upload a file
client.upload_file("/etc/passwd", "documents")

# Download a file
client.download_file("documents/passwd", "/tmp/downloaded_file.txt")

# Create a folder
client.create_folder("documents/new_folder")
client.upload_file("/etc/passwd", "documents/new_folder")

# Delete a file
client.delete_file("documents/passwd")

# Switch to a different account if needed
# client.authenticate_user(prompt_user=True)
"""


class RetryWithBackoff:
    def __init__(self, max_retries=5, initial_delay=1, max_delay=900, backoff_factor=2):  # max_delay = 15 minutes
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.error_counts: Dict[str, int] = {}  # Track error frequencies

    @staticmethod
    def should_retry(exception: Exception) -> bool:
        """Determine if the exception is retryable"""
        if isinstance(exception, requests.exceptions.HTTPError):
            try:
                error_data = exception.response.json().get('error', {})
                error_code = error_data.get('code', '')
                error_message = error_data.get('message', '')

                # Don't retry on access denied
                if error_code == 'accessDenied':
                    return False

                # Only skip retry for InternalServerError when message matches
                if error_code == 'InternalServerError' and 'Unable to find target address' in error_message:
                    return False

            except (ValueError, AttributeError) as e:
                # JSON decode error or missing response/json method
                pass

            # Standard HTTP errors to retry
            return exception.response.status_code in (408, 429, 500, 502, 503, 504)

        return isinstance(exception, (
            requests.exceptions.RequestException,
            requests.exceptions.ConnectionError,
            urllib3.exceptions.MaxRetryError,
            urllib3.exceptions.NewConnectionError
        ))

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = self.initial_delay
            last_exception = None

            for retry in range(self.max_retries + 1):
                try:
                    result = func(*args, **kwargs)
                    if retry > 0:
                        print(f"{datetime.now().astimezone().replace(microsecond=0).isoformat()} Request succeeded after {retry} retries",
                              file=sys.stderr)
                    return result
                except Exception as e:
                    last_exception = e
                    if retry == self.max_retries:
                        print(f"{datetime.now().astimezone().replace(microsecond=0).isoformat()} Max retries ({self.max_retries}) exceeded.",
                              file=sys.stderr)
                        raise

                    timestamp = datetime.now().astimezone().replace(microsecond=0).isoformat()
                    if isinstance(e, requests.exceptions.HTTPError):
                        response = e.response
                        print(f"{timestamp} HTTP Error Details:", file=sys.stderr)
                        print(f"  Request Method: {response.request.method}", file=sys.stderr)
                        print(f"  Request URL: {response.request.url}", file=sys.stderr)
                        print(f"  Response Status: {response.status_code}", file=sys.stderr)
                        print(f"  Response Headers: {dict(response.headers)}", file=sys.stderr)
                        print(f"  Response Body: {response.text}", file=sys.stderr)

                    if not self.should_retry(e):
                        raise

                    wait = min(delay, self.max_delay)
                    print(f"{timestamp} Network error occurred: {str(e)} (Exception type: {e.__class__.__name__})", file=sys.stderr)
                    print(f"{timestamp} Retrying in {wait} seconds... (Attempt {retry + 1}/{self.max_retries})", file=sys.stderr)
                    time.sleep(wait)
                    delay *= self.backoff_factor

            raise last_exception

        return wrapper


class OneDriveUserClient:
    # Configuration
    TOKEN_REFRESH_MINUTES = 20  # Refresh token if older than this many minutes
    MAX_RETRIES = 30
    INITIAL_DELAY = 1
    MAX_DELAY_SECS = 1000  # ~15 minutes
    BACKOFF_FACTOR = 2

    def __init__(self, client_id: str, client_secret: str,
                 account_type: Literal["business", "personal", "both"] = "both",
                 tenant_id: Optional[str] = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.account_type = account_type
        self.account = None
        self.access_token = None
        self.current_user = None
        self.token_obtained_time = None
        self.has_sharepoint_access = False  # Default to False
        self.organization_name = None
        self.organization_id = None
        self.account_id = None
        self.user_account_type = None  # To distinguish from self.account_type which is the app config

        if account_type == "business" and tenant_id:
            self.authority = f"https://login.microsoftonline.com/{tenant_id}"
        elif account_type == "personal":
            self.authority = "https://login.microsoftonline.com/consumers"
        else:
            self.authority = "https://login.microsoftonline.com/common"

        self.scope = ["Files.ReadWrite.All", "Files.ReadWrite", "Files.Read", "Files.Read.All", "User.Read", "Sites.Read.All"]
        self.endpoint = "https://graph.microsoft.com/v1.0"

        self.app = msal.ConfidentialClientApplication(
            client_id=self.client_id,
            client_credential=self.client_secret,
            authority=self.authority
        )

    def check_sharepoint_access(self):
        """Check if the authenticated user has SharePoint access"""
        try:
            org_info = self._make_request("GET", "/organization")
            if org_info.get("value"):
                org = org_info["value"][0]  # Get first org
                self.has_sharepoint_access = True
                self.user_account_type = "Business"
                self.organization_name = org.get("displayName", "Unknown")
                self.organization_id = org.get("id", "Unknown")
                print(f"{datetime.now().astimezone().replace(microsecond=0).isoformat()} SharePoint access detected (Organization: {self.organization_name}, ID: {self.organization_id})", file=sys.stderr)
        except:
            self.has_sharepoint_access = False
            self.organization_name = None
            self.organization_id = None
            self.user_account_type = "Personal"
            print(f"{datetime.now().astimezone().replace(microsecond=0).isoformat()} No SharePoint access detected", file=sys.stderr)

    def authenticate_user(self, prompt_user: bool = True) -> str:
        """Interactive authentication for a specific user"""
        current_time = datetime.now()

        # Always prompt for username if requested
        if prompt_user:
            print(f"\n{datetime.now().astimezone().replace(microsecond=0).isoformat()} Enter the email address for the OneDrive account you want to access:", file=sys.stderr)
            print("(Press Enter without typing anything to use default login flow)", file=sys.stderr)
            print("Email: ", end="", file=sys.stderr, flush=True)
            login_hint = input("").strip()
        else:
            login_hint = ""

        # Configure auth parameters based on account type
        auth_params = {
            "scopes": self.scope,
            "redirect_uri": "http://localhost:8000",
            "prompt": "select_account"  # Always show account picker
        }

        if login_hint:
            auth_params["login_hint"] = login_hint

        if self.account_type == "personal":
            print(f"{datetime.now().astimezone().replace(microsecond=0).isoformat()} Note: Using personal Microsoft account authentication", file=sys.stderr)
        elif self.account_type == "business":
            print(f"{datetime.now().astimezone().replace(microsecond=0).isoformat()} Note: Using business/school account authentication", file=sys.stderr)
        else:
            print(f"{datetime.now().astimezone().replace(microsecond=0).isoformat()} Note: Supporting both personal and business accounts", file=sys.stderr)

        # Start local server to receive auth code
        auth_code = None

        class AuthHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                nonlocal auth_code
                if "code=" in self.path:
                    auth_code = self.path.split("code=")[1].split("&")[0]

                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"Authentication successful! You can close this window.")

            def log_message(self, format, *args):
                return

        # Start local server
        server = HTTPServer(('localhost', 8000), AuthHandler)
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()

        # Generate auth URL and open browser
        auth_url = self.app.get_authorization_request_url(**auth_params)
        print(f"{datetime.now().astimezone().replace(microsecond=0).isoformat()} Opening browser for authentication...", file=sys.stderr)
        webbrowser.open(auth_url)

        # Wait for auth code
        while auth_code is None:
            pass

        # Shut down server
        server.shutdown()
        server.server_close()

        try:
            # Get token using auth code
            print(f"{datetime.now().astimezone().replace(microsecond=0).isoformat()} Acquiring token with authorization code...", file=sys.stderr)
            result = self.app.acquire_token_by_authorization_code(
                code=auth_code,
                scopes=self.scope,
                redirect_uri="http://localhost:8000"
            )

            if "access_token" in result:
                self.access_token = result["access_token"]
                self.token_obtained_time = current_time
                # Store the account information
                accounts = self.app.get_accounts()
                self.account = accounts[0] if accounts else None
                print(f"{datetime.now().astimezone().replace(microsecond=0).isoformat()} Token acquired successfully", file=sys.stderr)

                # Get current user info
                user_info = self._make_request("GET", "/me")
                self.current_user = user_info.get("userPrincipalName", "Unknown")
                self.account_id = user_info.get("id", "Unknown")

                print(f"{datetime.now().astimezone().replace(microsecond=0).isoformat()} Successfully authenticated as: {self.current_user} (Type: {self.user_account_type}, ID: {self.account_id})", file=sys.stderr)

                # After successful authentication, check SharePoint access
                self.check_sharepoint_access()
                return self.access_token

            else:
                error_msg = result.get('error_description', 'Unknown error')
                print(f"{datetime.now().astimezone().replace(microsecond=0).isoformat()} Failed to get token: {error_msg}", file=sys.stderr)
                raise Exception(f"Failed to get token: {error_msg}")

        except Exception as e:
            print(f"{datetime.now().astimezone().replace(microsecond=0).isoformat()} Authentication Error: {str(e)}", file=sys.stderr)
            print(f"{datetime.now().astimezone().replace(microsecond=0).isoformat()} Troubleshooting tips:", file=sys.stderr)
            print("1. Make sure your Azure AD app registration supports the correct account types", file=sys.stderr)
            print("2. Check if the account you're using matches the configured account type", file=sys.stderr)
            print("3. Verify that the redirect URI (http://localhost:8000) is registered in your Azure AD app", file=sys.stderr)
            print("4. Ensure the account has the necessary permissions", file=sys.stderr)
            raise

    def get_current_user(self) -> Optional[str]:
        """Get the email of the currently authenticated user"""
        return self.current_user

    def refresh_token(self, force_silent=True) -> bool:
        """
        Attempt to refresh the access token
        Args:
            force_silent: If True, only attempts silent refresh
        Returns:
            bool: True if refresh successful, False otherwise
        """
        current_time = datetime.now()
        print(f"{current_time.astimezone().replace(microsecond=0).isoformat()} Attempting silent token refresh...", file=sys.stderr)

        result = self.app.acquire_token_silent(self.scope, account=self.account)
        if result:
            self.access_token = result["access_token"]
            self.token_obtained_time = current_time
            print(f"{current_time.astimezone().replace(microsecond=0).isoformat()} Token refreshed silently", file=sys.stderr)
            return True
        elif not force_silent:
            print(f"{current_time.astimezone().replace(microsecond=0).isoformat()} Silent refresh failed, falling back to interactive auth", file=sys.stderr)
            try:
                self.authenticate_user(prompt_user=False)
                return True
            except Exception as e:
                print(f"{current_time.astimezone().replace(microsecond=0).isoformat()} Interactive refresh failed: {str(e)}", file=sys.stderr)
                return False
        return False

    def cleanup_tokens(self):
        """Cleanup authentication tokens and account info"""
        try:
            if self.account:
                print(f"{datetime.now().astimezone().replace(microsecond=0).isoformat()} Cleaning up authentication tokens...", file=sys.stderr)
                # Remove the account which invalidates its tokens
                self.app.remove_account(self.account)
                # Clear our stored values
                self.access_token = None
                self.account = None
                self.token_obtained_time = None
                print(f"{datetime.now().astimezone().replace(microsecond=0).isoformat()} Authentication cleanup completed", file=sys.stderr)
        except Exception as e:
            print(f"{datetime.now().astimezone().replace(microsecond=0).isoformat()} Warning: Token cleanup failed: {str(e)}", file=sys.stderr)

    @RetryWithBackoff(max_retries=MAX_RETRIES, initial_delay=INITIAL_DELAY, max_delay=MAX_DELAY_SECS, backoff_factor=BACKOFF_FACTOR)
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        current_time = datetime.now()

        # Check if token needs refresh based on age
        if (self.token_obtained_time and
                current_time - self.token_obtained_time > timedelta(minutes=self.TOKEN_REFRESH_MINUTES)):
            print(
                f"{current_time.astimezone().replace(microsecond=0).isoformat()} Token age: {current_time - self.token_obtained_time}",
                file=sys.stderr)
            self.refresh_token(force_silent=True)

        if not self.access_token:
            print(
                f"{current_time.astimezone().replace(microsecond=0).isoformat()} No token present, initiating authentication...",
                file=sys.stderr)
            self.authenticate_user(prompt_user=False)

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        response = requests.request(
            method,
            f"{self.endpoint}{endpoint}",
            headers=headers,
            **kwargs
        )

        # Handle 401 errors specifically
        if response.status_code == 401:
            print(
                f"{current_time.astimezone().replace(microsecond=0).isoformat()} Received 401 unauthorized, attempting token refresh...",
                file=sys.stderr)

            # Try silent refresh first
            if self.refresh_token(force_silent=True):
                # Retry the request with new token
                headers["Authorization"] = f"Bearer {self.access_token}"
                response = requests.request(
                    method,
                    f"{self.endpoint}{endpoint}",
                    headers=headers,
                    **kwargs
                )
            else:
                # If silent refresh failed, try interactive refresh
                if self.refresh_token(force_silent=False):
                    headers["Authorization"] = f"Bearer {self.access_token}"
                    response = requests.request(
                        method,
                        f"{self.endpoint}{endpoint}",
                        headers=headers,
                        **kwargs
                    )

        response.raise_for_status()
        return response.json() if response.content else {}

    def list_files(self, folder_path: str = "/", user_id: Optional[str] = None) -> List[Dict]:
        """
        List files and folders in the specified OneDrive folder

        Args:
            folder_path: Path to the folder (default: root)
            user_id: Optional user ID or email to access specific user's OneDrive

        Returns:
            List of files and folders with their metadata
        """
        from urllib.parse import quote

        # URL encode the path segments individually
        encoded_path = "/".join(quote(segment, safe='')
                              for segment in folder_path.split("/")
                              if segment)

        if user_id:
            # If listing files for another user
            if folder_path == "/" or folder_path == "":
                endpoint = f"/users/{user_id}/drive/root/children"
            else:
                endpoint = f"/users/{user_id}/drive/root:/{encoded_path}:/children"
        else:
            # If listing files for the authenticated user
            if folder_path == "/" or folder_path == "":
                endpoint = "/me/drive/root/children"
            else:
                endpoint = f"/me/drive/root:/{encoded_path}:/children"

        return self._make_request("GET", endpoint)["value"]

    def upload_file(self, file_path: str, destination_path: str, user_id: Optional[str] = None) -> Dict:
        """
        Upload a file to OneDrive

        Args:
            file_path: Local path to the file
            destination_path: Destination path in OneDrive
            user_id: Optional user ID or email to access specific user's OneDrive

        Returns:
            Uploaded file metadata
        """
        file_size = os.path.getsize(file_path)
        file_name = os.path.basename(file_path)

        user_prefix = f"/users/{user_id}" if user_id else "/me"

        if file_size <= 4 * 1024 * 1024:  # Small file upload (< 4MB)
            with open(file_path, 'rb') as file:
                endpoint = f"{user_prefix}/drive/root:/{destination_path}/{file_name}:/content"
                return self._make_request("PUT", endpoint, data=file)
        else:  # Large file upload
            # Create upload session
            endpoint = f"{user_prefix}/drive/root:/{destination_path}/{file_name}:/createUploadSession"
            upload_session = self._make_request("POST", endpoint)

            # Upload file in chunks
            chunk_size = 327680  # 320 KB chunks
            with open(file_path, 'rb') as file:
                for chunk_start in range(0, file_size, chunk_size):
                    chunk_end = min(chunk_start + chunk_size - 1, file_size - 1)
                    file.seek(chunk_start)
                    chunk_data = file.read(chunk_size)

                    headers = {
                        "Content-Length": str(len(chunk_data)),
                        "Content-Range": f"bytes {chunk_start}-{chunk_end}/{file_size}"
                    }

                    response = requests.put(
                        upload_session["uploadUrl"],
                        headers=headers,
                        data=chunk_data
                    )

                    if response.status_code == 201 or response.status_code == 200:
                        return response.json()

            raise Exception("Failed to upload file")

    def download_file(self, file_path: str, local_path: str, user_id: Optional[str] = None) -> None:
        """
        Download a file from OneDrive

        Args:
            file_path: Path to the file in OneDrive
            local_path: Local path to save the file
            user_id: Optional user ID or email to access specific user's OneDrive
        """
        user_prefix = f"/users/{user_id}" if user_id else "/me"
        endpoint = f"{user_prefix}/drive/root:/{file_path}:/content"
        response = requests.get(
            f"{self.endpoint}{endpoint}",
            headers={"Authorization": f"Bearer {self.access_token}"},
            stream=True
        )
        response.raise_for_status()

        with open(local_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

    def delete_file(self, file_path: str, user_id: Optional[str] = None) -> None:
        """
        Delete a file from OneDrive

        Args:
            file_path: Path to the file in OneDrive
            user_id: Optional user ID or email to access specific user's OneDrive
        """
        user_prefix = f"/users/{user_id}" if user_id else "/me"
        endpoint = f"{user_prefix}/drive/root:/{file_path}"
        self._make_request("DELETE", endpoint)

    def create_folder(self, folder_path: str, user_id: Optional[str] = None) -> Dict:
        """
        Create a new folder in OneDrive

        Args:
            folder_path: Path where to create the folder
            user_id: Optional user ID or email to access specific user's OneDrive

        Returns:
            Created folder metadata
        """
        parent_path = os.path.dirname(folder_path)
        folder_name = os.path.basename(folder_path)

        user_prefix = f"/users/{user_id}" if user_id else "/me"
        endpoint = f"{user_prefix}/drive/root:/{parent_path}:/children"
        data = {
            "name": folder_name,
            "folder": {},
            "@microsoft.graph.conflictBehavior": "rename"
        }

        return self._make_request("POST", endpoint, json=data)

    def get_sharing_link(self, file_path: str, user_id: Optional[str] = None, type: str = "view") -> str:
        """
        Create a sharing link for a file

        Args:
            file_path: Path to the file in OneDrive
            user_id: Optional user ID or email to access specific user's OneDrive
            type: Type of sharing link ("view" or "edit")

        Returns:
            Sharing link URL
        """
        user_prefix = f"/users/{user_id}" if user_id else "/me"
        endpoint = f"{user_prefix}/drive/root:/{file_path}:/createLink"

        data = {
            "type": type,
            "scope": "anonymous"
        }

        response = self._make_request("POST", endpoint, json=data)
        return response["link"]["webUrl"]

    def list_sharepoint_sites(self) -> List[Dict]:
        """List all SharePoint sites accessible to the user"""
        return self._make_request("GET", "/sites?search=*")["value"]

    def list_site_drives(self, site_id: str) -> List[Dict]:
        """List all document libraries (drives) in a SharePoint site"""
        return self._make_request("GET", f"/sites/{site_id}/drives")["value"]

    def list_site_files(self, site_id: str, drive_id: str, folder_path: str = "/") -> List[Dict]:
        """List files in a SharePoint site's document library"""
        from urllib.parse import quote

        if folder_path == "/" or folder_path == "":
            endpoint = f"/sites/{site_id}/drives/{drive_id}/root/children"
        else:
            # URL encode the path segments individually
            encoded_path = "/".join(quote(segment, safe='')
                                    for segment in folder_path.split("/")
                                    if segment)
            endpoint = f"/sites/{site_id}/drives/{drive_id}/root:/{encoded_path}:/children"
        try:
            response = self._make_request("GET", endpoint)

            # If we get a single folder object instead of a collection (happens with special paths)
            if 'value' not in response and 'folder' in response:
                print(f"{datetime.now().astimezone().replace(microsecond=0).isoformat()} Skipping special folder path: {folder_path}", file=sys.stderr)
                return []

            if 'value' not in response:
                print(f"{datetime.now().astimezone().replace(microsecond=0).isoformat()} Unexpected API response format:", file=sys.stderr)
                print(f"Endpoint: {endpoint}", file=sys.stderr)
                print(f"Response: {json.dumps(response, indent=2)}", file=sys.stderr)
                raise ValueError(f"Unexpected API response format - missing 'value' key in response")

            return response["value"]

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"{datetime.now().astimezone().replace(microsecond=0).isoformat()} Path not found, skipping: {folder_path}", file=sys.stderr)
                return []
            raise

    def get_total_items(self) -> Tuple[int, int, int, int]:
        """Get total count of items from drive statistics"""
        onedrive_info = self._make_request("GET", "/me/drive")
        onedrive_used = onedrive_info.get('quota', {}).get('used', 0)
        onedrive_remaining = onedrive_info.get('quota', {}).get('remaining', 0)

        # Only try SharePoint if we have access
        if self.has_sharepoint_access:
            sharepoint_used = 0
            sharepoint_remaining = 0

            sites = self.list_sharepoint_sites()
            for site in sites:
                site_id = site["id"]
                drives = self.list_site_drives(site_id)
                for drive in drives:
                    drive_info = self._make_request("GET", f"/sites/{site_id}/drives/{drive['id']}")
                    sharepoint_used += drive_info.get('quota', {}).get('used', 0)
                    sharepoint_remaining += drive_info.get('quota', {}).get('remaining', 0)
        else:
            sharepoint_used = 0
            sharepoint_remaining = 0

        return onedrive_used, onedrive_remaining, sharepoint_used, sharepoint_remaining



def main():
    print(f"----OneDriveAutomation----", file=sys.stderr)

    # Initialize the client
    client = OneDriveUserClient(
        account_type="both",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    )

    client.authenticate_user(prompt_user=True)

    def list_files_recursively(client, folder_path="/", line_count=0, max_lines=None):
        """Returns tuple of (line_count, total_bytes, file_count)"""
        if max_lines and line_count >= max_lines:
            return line_count, 0, 0

        files = client.list_files(folder_path)
        dir_total_bytes = 0
        dir_file_count = 0

        for file in files:
            # Skip if we've hit the limit
            if max_lines and line_count >= max_lines:
                return line_count, dir_total_bytes, dir_file_count

            # Print progress every 500 files
            if line_count > 0 and line_count % 500 == 0:
                print(f"{datetime.now().astimezone().replace(microsecond=0).isoformat()} {line_count} files processed", file=sys.stderr)

            # Basic properties
            name = file.get('name', 'Unknown').replace('\t', ' ')
            full_path = f"{folder_path}/{name}".replace('//', '/')
            file_type = 'Folder' if 'folder' in file else 'File'

            # Handle folders vs files differently for size and count
            if 'folder' in file:
                new_path = f"{folder_path}/{name}".replace('//', '/')
                line_count, folder_bytes, folder_files = list_files_recursively(
                    client, new_path, line_count, max_lines)
                file['size'] = folder_bytes
                file['childCount'] = folder_files
                dir_total_bytes += folder_bytes
                dir_file_count += folder_files
            else:
                dir_total_bytes += file.get('size', 0)
                dir_file_count += 1

            # Size (both formatted and raw bytes)
            size_bytes = file.get('size', 0)
            if size_bytes < 1024:
                size = f"{size_bytes}B"
            elif size_bytes < 1024 * 1024:
                size = f"{size_bytes / 1024:.1f}KB"
            else:
                size = f"{size_bytes / (1024 * 1024):.1f}MB"

            # Dates
            modified = file.get('lastModifiedDateTime', 'Unknown')
            created = file.get('createdDateTime', 'Unknown')

            # Owner and last modifier
            owner = file.get('createdBy', {}).get('user', {}).get('displayName', 'Unknown').replace('\t', ' ')
            last_modifier = file.get('lastModifiedBy', {}).get('user', {}).get('displayName', 'Unknown').replace('\t', ' ')

            # Sharing status
            shared = 'Yes' if file.get('shared', {}).get('scope') else 'No'

            # File properties
            mime_type = file.get('file', {}).get('mimeType', 'N/A').replace('\t', ' ')
            hash_value = file.get('file', {}).get('hashes', {}).get('sha256Hash', 'N/A').replace('\t', ' ')

            # Sharing properties
            share_scope = file.get('shared', {}).get('scope', 'Not shared').replace('\t', ' ')
            share_owner = str(file.get('shared', {}).get('owner', 'N/A')).replace('\t', ' ')

            # File system info
            client_created = file.get('fileSystemInfo', {}).get('createdDateTime', 'Unknown')
            client_modified = file.get('fileSystemInfo', {}).get('lastModifiedDateTime', 'Unknown')

            # Deleted status
            deleted = 'Yes' if 'deleted' in file else 'No'

            # Child count (N/A for files)
            child_count = str(file.get('folder', {}).get('childCount', 'N/A')) if file_type == 'Folder' else 'N/A'

            # Full metadata
            metadata = file.copy()
            metadata.pop('@microsoft.graph.downloadUrl', None)  # Remove if exists, screws up idempotency & privacy
            metadata_json = json.dumps(metadata, sort_keys=True).replace('\t', ' ')

            print(
                f"N/A\t"  # Site Name field for OneDrive files
                f"{full_path}\t"
                f"{file_type}\t"
                f"{size}\t"
                f"{size_bytes}\t"
                f"{folder_files if 'folder' in file else 'N/A'}\t"
                f"{modified}\t"
                f"{created}\t"
                f"{owner}\t"
                f"{last_modifier}\t"
                f"{shared}\t"
                f"{mime_type}\t"
                f"{hash_value}\t"
                f"{share_scope}\t"
                f"{share_owner}\t"
                f"{client_created}\t"
                f"{client_modified}\t"
                f"{deleted}\t"
                f"{child_count}\t"
                f"{metadata_json}"
            )

            line_count += 1

        return line_count, dir_total_bytes, dir_file_count

    def process_sharepoint_folder(site_id, drive_id, site_name, drive_name, folder_path="/", line_count=0, max_lines=None):
        if max_lines and line_count >= max_lines:
            return line_count, 0, 0

        files = client.list_site_files(site_id, drive_id, folder_path)
        dir_total_bytes = 0
        dir_file_count = 0

        for file in files:
            if max_lines and line_count >= max_lines:
                return line_count, dir_total_bytes, dir_file_count

            # Print progress every 500 files
            if line_count > 0 and line_count % 500 == 0:
                print(f"{datetime.now().astimezone().replace(microsecond=0).isoformat()} {line_count} SharePoint files processed", file=sys.stderr)

            # Basic properties
            name = file.get('name', 'Unknown').replace('\t', ' ')
            full_path = f"/{site_name}/{drive_name}{folder_path}/{name}".replace('//', '/')
            file_type = 'Folder' if 'folder' in file else 'File'

            # Handle folders vs files differently for size and count
            if 'folder' in file:
                new_path = f"{folder_path}/{name}".replace('//', '/')
                line_count, folder_bytes, folder_files = process_sharepoint_folder(
                    site_id, drive_id, site_name, drive_name, new_path, line_count, max_lines)
                file['size'] = folder_bytes
                file['childCount'] = folder_files
                dir_total_bytes += folder_bytes
                dir_file_count += folder_files
            else:
                dir_total_bytes += file.get('size', 0)
                dir_file_count += 1

            # Size (both formatted and raw bytes)
            size_bytes = file.get('size', 0)
            if size_bytes < 1024:
                size = f"{size_bytes}B"
            elif size_bytes < 1024 * 1024:
                size = f"{size_bytes / 1024:.1f}KB"
            else:
                size = f"{size_bytes / (1024 * 1024):.1f}MB"

            # Dates
            modified = file.get('lastModifiedDateTime', 'Unknown')
            created = file.get('createdDateTime', 'Unknown')

            # Owner and last modifier
            owner = file.get('createdBy', {}).get('user', {}).get('displayName', 'Unknown').replace('\t', ' ')
            last_modifier = file.get('lastModifiedBy', {}).get('user', {}).get('displayName', 'Unknown').replace('\t', ' ')

            # Sharing status
            shared = 'Yes' if file.get('shared', {}).get('scope') else 'No'

            # File properties
            mime_type = file.get('file', {}).get('mimeType', 'N/A').replace('\t', ' ')
            hash_value = file.get('file', {}).get('hashes', {}).get('sha256Hash', 'N/A').replace('\t', ' ')

            # Sharing properties
            share_scope = file.get('shared', {}).get('scope', 'Not shared').replace('\t', ' ')
            share_owner = str(file.get('shared', {}).get('owner', 'N/A')).replace('\t', ' ')

            # File system info
            client_created = file.get('fileSystemInfo', {}).get('createdDateTime', 'Unknown')
            client_modified = file.get('fileSystemInfo', {}).get('lastModifiedDateTime', 'Unknown')

            # Deleted status
            deleted = 'Yes' if 'deleted' in file else 'No'

            # Child count (N/A for files)
            child_count = str(file.get('folder', {}).get('childCount', 'N/A')) if file_type == 'Folder' else 'N/A'

            # Full metadata (remove download URL and convert to JSON)
            metadata = file.copy()
            metadata.pop('@microsoft.graph.downloadUrl', None)  # Remove if exists, screws up idempotency & privacy
            metadata_json = json.dumps(metadata, sort_keys=True).replace('\t', ' ')

            print(
                f"{site_name}\t"
                f"{full_path}\t"
                f"{file_type}\t"
                f"{size}\t"
                f"{size_bytes}\t"
                f"{folder_files if 'folder' in file else 'N/A'}\t"
                f"{modified}\t"
                f"{created}\t"
                f"{owner}\t"
                f"{last_modifier}\t"
                f"{shared}\t"
                f"{mime_type}\t"
                f"{hash_value}\t"
                f"{share_scope}\t"
                f"{share_owner}\t"
                f"{client_created}\t"
                f"{client_modified}\t"
                f"{deleted}\t"
                f"{child_count}\t"
                f"{metadata_json}"
            )

            line_count += 1

        return line_count, dir_total_bytes, dir_file_count

    try:
        max_lines = None  # Set to None for unlimited lines or a number for a limit

        # Print headers once for all files
        start_info = f"Started: {datetime.now().astimezone().replace(microsecond=0).isoformat()} ({client.current_user} / {client.user_account_type} / ID: {client.account_id}"
        if client.has_sharepoint_access:
            start_info += f" / Organization: {client.organization_name} / Org ID: {client.organization_id}"
        start_info += ")"
        print(start_info)

        # Get drive statistics
        onedrive_used, onedrive_remaining, sharepoint_used, sharepoint_remaining = client.get_total_items()

        # OneDrive stats
        onedrive_used_gb = onedrive_used / (1024 * 1024 * 1024)
        onedrive_remaining_gb = onedrive_remaining / (1024 * 1024 * 1024)
        print(f"OneDrive Usage: {onedrive_used_gb:.1f}GB used, {onedrive_remaining_gb:.1f}GB remaining ({onedrive_used} bytes / {onedrive_used + onedrive_remaining} bytes used)")

        # SharePoint stats
        sharepoint_used_gb = sharepoint_used / (1024 * 1024 * 1024)
        sharepoint_remaining_gb = sharepoint_remaining / (1024 * 1024 * 1024)
        print(f"SharePoint Usage: {sharepoint_used_gb:.1f}GB used, {sharepoint_remaining_gb:.1f}GB remaining ({sharepoint_used} bytes / {sharepoint_used + sharepoint_remaining} bytes used)")

        print("\nFiles in OneDrive and SharePoint (Recursive):")
        print("Site\tPath\tType\tSize\tBytes\tFilecount\tModified\tCreated\tOwner\tLast Modified By\tShared\tMIME Type\tHash\tShare Scope\tShare Owner\tClient Created\tClient Modified\tDeleted\tChild Count\tMetadata")
        print("-" * 200)

        # Process OneDrive files
        print(f"{datetime.now().astimezone().replace(microsecond=0).isoformat()} Processing OneDrive files...", file=sys.stderr)
        total_lines, _, _ = list_files_recursively(client, max_lines=max_lines)

        # Only process SharePoint if we have access
        if client.has_sharepoint_access:
            print(f"{datetime.now().astimezone().replace(microsecond=0).isoformat()} Processing SharePoint files...", file=sys.stderr)
            sites = client.list_sharepoint_sites()

            for site in sites:
                site_id = site["id"]
                site_name = site.get("displayName", "Unknown")

                print(f"{datetime.now().astimezone().replace(microsecond=0).isoformat()} Processing SharePoint site: {site_name}", file=sys.stderr)

                # Get all document libraries in the site
                drives = client.list_site_drives(site_id)

                for drive in drives:
                    drive_id = drive["id"]
                    drive_name = drive.get("name", "Unknown")

                    print(f"{datetime.now().astimezone().replace(microsecond=0).isoformat()} Processing document library: {drive_name}", file=sys.stderr)

                    total_lines, _, _ = process_sharepoint_folder(site_id, drive_id, site_name, drive_name, "/", total_lines, max_lines)
                    if max_lines and total_lines >= max_lines:
                        break

                if max_lines and total_lines >= max_lines:
                    break

        else:
            print(f"{datetime.now().astimezone().replace(microsecond=0).isoformat()} Skipping SharePoint processing - no access", file=sys.stderr)

    except (Exception, KeyboardInterrupt) as e:
        print("-" * 200)
        print(f"Aborted: {datetime.now().astimezone().replace(microsecond=0).isoformat()}")
        raise
    finally:
        print("-" * 200)
        if client:  # Ensure client exists before cleanup
            client.cleanup_tokens()
        if 'e' not in locals():  # ie, "Aborted:" not already printed
            print(f"Finished: {datetime.now().astimezone().replace(microsecond=0).isoformat()}")


    # POSSIBLE FUTURE DIRECTIONS:
    #
    # A few other aspects I considered while writing it:
    # - Proper tail recursion for folder traversal
    # - Early termination when hitting limits
    # - Clean state propagation up the call stack
    # - No shared mutable state between recursive calls
    # - Clear parameter passing at each recursive step
    #
    # Though if this were production code, I might add:
    # - Error handling for API rate limits
    # - Progress reporting for deep hierarchies
    # - Memory management for very large directories
    # - Ability to resume from a specific path
    # - Concurrent processing for large hierarchies (though this would require careful consideration of thread safety)
    #
    # From my knowledge of the Microsoft Graph API, it doesn't expose IP address information directly in the standard file metadata like we're currently retrieving.
    #
    # However, there are two potential ways to get IP information, but they require different API endpoints and permissions:
    #
    # - Audit Logs - The Microsoft 365 Audit Log can track SharePoint/OneDrive activities with IP addresses
    # - Sign-in Logs - Contains IP information for user authentications
    #
    # These would require:
    # - Different API endpoints
    # - Additional permissions
    # - Audit logging to be enabled
    # - Different time windows (audit data is typically only retained for a limited time)
    #
    # Would you like me to show you how to query either of these log sources? They'd need to be separate queries as they're not part of the file/folder metadata we're currently accessing.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
