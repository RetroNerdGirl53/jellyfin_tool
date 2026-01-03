Jellyfin User Management Tool (CLI)

This tool provides a high-performance command-line interface for managing Jellyfin users based on their activity levels. It allows administrators to automatically suspend or delete users who have been inactive for a specified number of days, utilizing direct database queries for maximum speed—even on servers with high user count as compared to using API calls alone.
Important: Database Syncing

You must restart your Jellyfin server before running this tool if you want the most up-to-date activity data. Jellyfin often holds database writes in memory; a restart forces the server to commit all "Last Seen" and "Playback" data to the .db files on disk, ensuring the script reads accurate information.
Database Locations

The tool requires paths to library.db and jellyfin.db. Default locations typically vary by operating system:
OS / Distro	Typical Path
Windows	C:\Users\<User>\AppData\Local\jellyfin\data\
Linux (Generic)	/var/lib/jellyfin/data/
Docker	/config/data/ (inside your mapped volume)
MacOS	/Users/<User>/.config/jellyfin/data/
Installation

Ensure you have Python 3.x installed along with the required libraries:
Bash

pip install pandas requests

Usage & Arguments

The script uses a standard CLI structure: python jellyfin2.py [library_db] [jellyfin_db] --api-key [KEY] [OPTIONS]
Required Arguments

    library_db: Path to the library.db file (used for playback history).

    jellyfin_db: Path to the jellyfin.db file (used for user accounts/logins).

    --api-key: Your Jellyfin API key (generated in Dashboard > API Keys).

Optional Configuration

    --server: Your Jellyfin URL (Default: http://localhost:8096).

    --days: The inactivity threshold (Default: 30).

    --mode: Choose the activity criteria.

        playback: Bases inactivity on the last time a user played media.

        login: Bases inactivity on the last time a user logged into the server.

    --delete: If flagged, the tool will permanently delete users instead of suspending them.

    --dry-run: Highly recommended. Shows exactly what the script would do without making any API changes.

Targeting Specific Users

You can target the entire database (default) or restrict the script using one of these:

    --username [NAME]: Run the script for a single specific user.

    --userlist [FILE]: Run the script against a list of usernames in a .txt file (one per line).

Examples

1. Dry run: See who hasn't logged in for 90 days
Bash

python jellyfin2.py ./library.db ./jellyfin.db --api-key YOUR_KEY --days 90 --mode login --dry-run

2. Suspend users inactive (no playback) for 30 days
Bash

python jellyfin2.py /var/lib/jellyfin/data/library.db /var/lib/jellyfin/data/jellyfin.db --api-key YOUR_KEY

3. Delete users listed in a file
Bash

python jellyfin2.py ./library.db ./jellyfin.db --api-key YOUR_KEY --userlist to_remove.txt --delete

Logic Notes

    No History: If a user has no record of a login or playback (depending on the mode), the script will skip them by default to avoid accidental deletions of new or system accounts.

    Suspension vs. Deletion: Suspension sets the IsDisabled policy to True. Deletion is an unrecoverable API call that removes the user and their associated data from Jellyfin.

    >>>>>Technical Note on Database Accuracy: Jellyfin uses SQLite's WAL (Write-Ahead Logging) mode. Recent activity may be stored in jellyfin.db-wal rather than the main database file. To ensure the script doesn't accidentally suspend an active user, restart Jellyfin to "checkpoint" the data into the main file before running this tool.<<<<<

Lastly there is a cron automator script jf_maintenance.sh that sets a cron job to automatically sync the database and run the script with your chosen options at a time and date of your choosing.
