import sqlite3
import pandas as pd
#import numpy as np
import time
import matplotlib
from matplotlib import pyplot as plt
import seaborn as sns

library_path=input("what is your library.db database path? >>> ")
jellyfin_path=input("what is your jellyfin.db database path? >>> ")
conn=sqlite3.connect(jellyfin_path)
cursor=conn.cursor()

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
            whatami=input("WHAT ARE YOU?! WHAT ARE YOU?! ***puts bread on either side of your head***")
            if whatami == "an idiot sandwich" or "An idiot sandwich" or "An Idiot Sandwich":
                 print("yes you are now go back to the input prompt and give me a legitimate Y or N")
        
        # 3. If we get here, they messed up. The loop restarts.
        print("Invalid input. Please enter 'Y' or 'N'. DON'T be an idiot sandwich.")

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

selected_user=input("What user would you like to query? >>> ")
try:
    print(f"The Usernames associated id is: {username_map[selected_user]}")
except KeyError:
    print("That user doesn't exist dumbass. Did you spell it right? Hukked on Foniks Werkked fer U!")
    selected_user=input("what user would you like to recommend? >>> ")

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
# Define your column names manually
cols = ['Title', 'Plays', 'Last Played', 'isFavorite', 'Played']

# Create the DataFrame
df = pd.DataFrame(selected_data, columns=cols)
conn.close()
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

