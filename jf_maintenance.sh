#!/bin/bash

# --- CONFIGURATION (Edit these) ---
PYTHON_SCRIPT="/path/to/jellytool.py"
LIB_DB="/path/to/library.db"
JF_DB="/path/to/jellyfin.db"
API_KEY="your_api_key_here"
DAYS=30
MODE="login" # or playback
ACTION="suspend" # or delete
LOG_FILE="/var/log/jellyfin_cleanup.log"

echo "--- Starting Jellyfin Maintenance: $(date) ---" >> $LOG_FILE

# 1. Sync the Database (Restart Service)
echo "Restarting Jellyfin to sync WAL files..." >> $LOG_FILE
systemctl restart jellyfin

# Give the OS a few seconds to finalize file handles
sleep 5

# 2. Run the Python Tool
echo "Running cleanup script in $MODE mode..." >> $LOG_FILE

# Construct the command
CMD="python3 $PYTHON_SCRIPT \"$LIB_DB\" \"$JF_DB\" --api-key $API_KEY --days $DAYS --mode $MODE"
if [ "$ACTION" == "delete" ]; then
    CMD="$CMD --delete"
fi

# Execute and pipe output to log
eval $CMD >> $LOG_FILE 2>&1

echo "Maintenance complete: $(date)" >> $LOG_FILE
echo "-------------------------------------------" >> $LOG_FILE
