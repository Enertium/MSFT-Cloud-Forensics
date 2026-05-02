# ONEDRIVE FORENSIC FILESYSTEM METADATA ANALYZER AND DOCUMENTER

Hi Claude! You're my software engineering computer science graduate. Let me explain what we built.

## Purpose
A forensic dump utility for Office 365 that captures and compares complete filesystem metadata states, enabling reproducible snapshot analysis of changes over time. Essential for auditing, compliance, and chain-of-custody requirements.

## Core Functionality
- Authenticates to Microsoft 365 tenant services securely
- Recursively traverses OneDrive and SharePoint document libraries 
- Captures comprehensive file/folder metadata with focus on forensic attributes
- Handles large file systems (100k+ items) reliably with retry logic
- Generates tab-separated dumps for stable diffing
- Maintains idempotent output for valid state comparisons
- Supports both personal and business accounts

## Key Architecture Points
- Uses Microsoft Graph API via MSAL authentication 
- Separates data output (stdout) from diagnostics (stderr)
- Two main recursion functions handle OneDrive/SharePoint traversal
- All file operations go through OneDriveUserClient abstraction
- Clean separation between auth, traversal, and output concerns

## Critical Modules
- OneDriveUserClient: Core authentication and API interface
- RetryWithBackoff: Network resilience with exponential backoff
- list_files_recursively: OneDrive tree traversal
- process_sharepoint_folder: SharePoint traversal
- main: Orchestration and output formatting

## Technical Solutions
- Token refresh: Silent refresh every 20 mins, fallback to interactive
- Network resilience: 20 retries up to 15 min delays
- Path encoding: URL-safe special character handling
- Auth cleanup: Proper token/session cleanup on crashes
- Error handling: Smart retry on appropriate errors only
- Idempotency: Metadata normalization for comparison

## Engineering Principles
- Keep diagnostic logging separate from data output
- Handle network/auth issues gracefully for long-running processes
- Make output reproducible through careful metadata handling
- Fail gracefully and clean up properly
- Don't retry permanent errors
- Document all idempotency decisions

Would you like to see the implementation details in the code?
