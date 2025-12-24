import sqlite3
import pandas as pd
#import numpy as np
import time
import matplotlib
from matplotlib import pyplot as plt
import seaborn as sns

Bold_SlowBlnk_Red = "\033[31;1;5m"
Bold_Bright_White = "\033[97;1;4m"
Cyan = "\033[96m"
RESET="\033[0m"

def countdown(seconds):
    """Counts down on the same line."""
    while seconds > 0:
        # 1. Print the number
        # end="\r" prevents the new line
        # flush=True forces it to show up immediately
        print(f"Melting Down In: {seconds} ", end="\r", flush=True)

        # 2. Wait
        time.sleep(1)

        # 3. Decrement
        seconds -= 1

    # Optional: Clear the line when done
    print(" " * 20, end="\r")
    print(f"{Bold_SlowBlnk_Red}You're in trouble now!{RESET}")

def get_yes_no(question):
    """Asks a question and forces a Y/N answer."""
    while True:
        # 1. Get input, strip spaces, and make it lowercase
        response = input(f"{question} (Y/N) >>> ").strip().lower()

        # 2. Check the answer
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        elif response in ['idiot sandwich', 'Idiot sandwich', 'Idiot Sandwich']:
            print()
            print(f"{Bold_SlowBlnk_Red}Chef Ramsay mode activated{RESET}")
            print()
            countdown(10)
            whatami=input(f"WHAT ARE YOU?! {Bold_Bright_White}WHAT ARE YOU?!{RESET} ***puts bread on either side of your head*** >>> ")
            if whatami.lower() == "an idiot sandwich" or "idiot sandwich" or "a idiot sandwich":
                 print("yes you are now go back to the input prompt")
                 print()
                 time.sleep(2)
        # 3. If we get here, they messed up. The loop restarts.
        print(f"{Cyan}*Sigh*{RESET} Please enter 'Y' or 'N'. DON'T be an idiot sandwich.")

def user_id_connect():
    jellyfin_path=input("what is your jellyfin.db database path? >>> ")
    conn=sqlite3.connect(jellyfin_path)
    cursor=conn.cursor()

    print("connected to jellyfin database")
    time.sleep(0.5)

    cursor.execute("SELECT Username, InternalId FROM users")
    username_map = {}
    for row in cursor:
        key, value = row  # Unpacks the tuple (name, id)
        username_map[key]=value
    conn.close()

    print("username/userid info pulled and mapped")
    time.sleep(0.2)
    return username_map

def library_db_query():
    library_path=input("what is your library.db database path? >>> ")
    conn=sqlite3.connect(library_path)

    print("Jellyfin library database connected.")
    time.sleep(0.3)

    cursor=conn.cursor()

    #debug code
    #print("cursor object created")

    # We use a multi-line f-string to make the complex query readable
    query = f"""
    SELECT
        T.Name,
        U.PlayCount,
        U.LastPlayedDate,
        U.isFavorite,
        U.Played
    FROM UserDatas U
    JOIN TypedBaseItems T ON U.key = T.UserDataKey
    WHERE U.UserId = {username_map[selected_user]}
    AND U.PlayCount > 0
    """


    cursor.execute(query)

    selected_data = cursor.fetchall()
    conn.close()
    return selected_data

username_map = user_id_connect() #call the function
selected_user=input("What user would you like to query? >>> ")
try:
    print(f"The Usernames associated id is: {username_map[selected_user]}")
except KeyError:
    print("That user doesn't exist dumbass. Did you spell it right? Hukked on Foniks Werkked fer U!")
    selected_user=input("what user would you like to recommend? >>> ")

library_data=library_db_query()
# Define your column names manually
cols = ['Title', 'Plays', 'Last Played', 'isFavorite', 'Played']

# Create the DataFrame
df = pd.DataFrame(library_data, columns=cols)
# Clean the 'Plays' column
df['Plays'] = df['Plays'].fillna(0)
df['Plays'] = df['Plays'].astype('int32')

# Clean the 'isFavorite' column
df['isFavorite'] = df['isFavorite'].fillna(0)
df['isFavorite'] = df['isFavorite'].astype('int32')

# Clean the 'Played' column
df['Played'] = df['Played'].fillna(0)
df['Played'] = df['Played'].astype('int32')
# Create a new column 'Plays_Scaled'
df['Plays_Scaled'] = (df['Plays'] - df['Plays'].min()) / (df['Plays'].max() - df['Plays'].min())
# Now 14 plays becomes 1.0, and 1 play becomes 0.0

average_plays=df['Plays'].mean()
average_favorite=df['isFavorite'].mean()
#print(df.describe()) <---user doesn't probably need this, only good for data scientists
ax = sns.regplot(x='Plays_Scaled', y='isFavorite', data=df)
plt.title(f"{selected_user}'s Relative Play Count vs Favorite Status")
ax.set_xlabel("Relative Play Count")
ax.set_ylabel("Favorite or no?")
ax.set_xticks([0, 0.5, 1])
ax.set_xticklabels(["None", "More", "Most"])
ax.set_yticks([0, 1])
ax.set_yticklabels(["No", "Yes"])
plt.show()
# Jitter=True spreads the dots out so you can see them all
ax=sns.stripplot(x='isFavorite', y='Plays_Scaled', data=df, jitter=True)
ax.set_xlabel("Favorite or no?")
ax.set_ylabel("Relative Play Count")
ax.set_xticks([0, 1])
ax.set_xticklabels(["No", "Yes"])
ax.set_yticks([0, 0.5, 1])
ax.set_yticklabels(["None", "More", "Most"])
plt.title(f"{selected_user}'s Favorite Status vs Relative Play Count")
plt.show()

print(f"The Basics\n{df.describe()}")
print()
print()
print("=======================================================================================================")
print()
print()
print(f"Average plays: {average_plays}\nAverage favs: {average_favorite}")
print()
print(f"Favorited titles count = {df['isFavorite'].sum()}")
print()
print(f"Total number of titles played for {selected_user}: {df['Plays'].sum()}")
print()
print()
print(f"Correlated or no? Negative is inverse proportional, 0 is no correlation, \nPositive is Proportional. Values are -1 through 1.\nRemember correlation does not equal causation >>> \n \n {df[['Plays', 'isFavorite']].corr()}")
describe=df.describe()
if get_yes_no("Would you like to save all this awesomeness to the current directory? Enter Y or N >>>"):
    print(f"Saving file {selected_user}_stats.csv to current directory")
    describe.to_csv(f"{selected_user}_stats.csv")
    print(f"file {selected_user}_stats.csv written to current directory")
else:
    print("Saving skipped. Have a nice day")

