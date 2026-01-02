import sqlite3
import time
import argparse
import requests
import pandas as pd
import datetime
import sys

# --- UI / Formatting ---
Bold_SlowBlnk_Red = "\033[31;1;5m"
Bold_Bright_White = "\033[97;1;4m"
Cyan = "\033[96m"
RESET = "\033[0m"

# --- 1. ARGPARSE SETUP ---
parser = argparse.ArgumentParser(description="Jellyfin Administrative User Manager")

# Positional Arguments
parser.add_argument("library_db", help="Path to library.db")
parser.add_argument("jellyfin_db", help="Path to jellyfin.db")

# API and Action Config
parser.add_argument("--server", default="http://localhost:8096", help="Jellyfin server URL")
parser.add_argument("--api-key", required=True, help="Jellyfin API Key")
parser.add_argument("--days", type=int, default=30, help="Inactivity threshold in days")
parser.add_argument("--mode", choices=['playback', 'login'], default='playback',
                    help="Criteria for activity: 'playback' (default) or 'login'")

# Logic Flags
parser.add_argument("--delete", action="store_true", help="PERMANENTLY delete users instead of suspending")
parser.add_argument("--dry-run", action="store_true", help="Show what would happen without making API changes")

# Hidden Easter Egg
parser.add_argument("--idiot-sandwich", action="store_true", help=argparse.SUPPRESS)

# Mutually Exclusive Group
users_group = parser.add_mutually_exclusive_group()
users_group.add_argument("--username", help="Run against a single username")
users_group.add_argument("--userlist", help="Path to a text file of usernames")

args = parser.parse_args()

# --- 2. FUNCTIONS ---

def chef_ramsay_mode():
    print(f"\n{Bold_SlowBlnk_Red}Chef Ramsay mode activated{RESET}\n")
    secret_phrases = ["an idiot sandwich", "idiot sandwich", "a idiot sandwich"]
    prompt = f"WHAT ARE YOU?! {Bold_Bright_White}WHAT ARE YOU?!{RESET} ***puts bread on either side of your head*** >>> "
    if input(prompt).strip().lower() in secret_phrases:
         print("Yes you are. Now get back to the terminal.\n")
         time.sleep(2)

def get_user_data_maps():
    """Maps Username to GUID, InternalId, and LastLoginDate."""
    conn = sqlite3.connect(args.jellyfin_db)
    cursor = conn.cursor()
    # We pull LastLoginDate directly from the Users table here
    cursor.execute("SELECT Username, Id, InternalId, LastLoginDate FROM Users")

    guid_map = {}
    internal_map = {}
    login_map = {}

    for name, guid, i_id, login_date in cursor:
        guid_map[name] = guid
        internal_map[name] = i_id
        login_map[name] = login_date

    conn.close()
    return guid_map, internal_map, login_map

def get_last_played_bulk():
    """Bulk SQL query for newest play date."""
    conn = sqlite3.connect(args.library_db)
    query = "SELECT UserId, MAX(LastPlayedDate) FROM UserDatas WHERE PlayCount > 0 GROUP BY UserId"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return dict(zip(df.iloc[:,0], df.iloc[:,1]))

def manage_user(guid, username, action="suspend"):
    headers = {"X-Emby-Token": args.api_key}
    if action == "delete":
        url, method = f"{args.server}/Users/{guid}", requests.delete
        payload = None
    else:
        url, method = f"{args.server}/Users/{guid}/Policy", requests.post
        headers["Content-Type"], payload = "application/json", {"IsDisabled": True}

    if args.dry_run:
        print(f"{Cyan}[DRY RUN]{RESET} Would have {action.upper()}ED: {username}")
        return

    try:
        response = method(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 204:
            print(f"{Bold_SlowBlnk_Red}[ACTION]{RESET} {action.upper()}ED: {username}")
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")

# --- 3. EXECUTION ---

if args.idiot_sandwich: chef_ramsay_mode()

guid_map, internal_map, login_map = get_user_data_maps()
playback_map = get_last_played_bulk() if args.mode == 'playback' else {}

# Determine targets
if args.username:
    targets = [args.username]
elif args.userlist:
    with open(args.userlist, 'r') as f: targets = [line.strip() for line in f]
else:
    targets = list(guid_map.keys())

threshold_date = datetime.datetime.now() - datetime.timedelta(days=args.days)
action_type = "delete" if args.delete else "suspend"

print(f"{Cyan}Running in {args.mode} mode. Threshold: {args.days} days.{RESET}\n")

for user in targets:
    if user not in guid_map: continue

    # 1. Pick the date string based on the selected mode
    if args.mode == 'playback':
        date_str = playback_map.get(internal_map[user])
    else:
        date_str = login_map.get(user)

    # 2. Logic for NO history exists (Default to doing nothing)
    if not date_str:
        print(f"Skipping {user}: No {args.mode} history found.")
        continue

    # 3. Date Parsing and Comparison
    try:
        clean_date = date_str.split('.')[0].replace('T', ' ').replace('Z', '')
        dt_object = datetime.datetime.strptime(clean_date, '%Y-%m-%d %H:%M:%S')

        if dt_object < threshold_date:
            print(f"User {user} is inactive (Last {args.mode}: {clean_date})")
            manage_user(guid_map[user], user, action=action_type)

    except Exception as e:
        print(f"Error parsing date for {user}: {e}")

print(f"\n{Cyan}Task Complete.{RESET}")
