import sqlite3
import pandas as pd

# Step 1. Load data file
df = pd.read_csv('instance/data.csv')
# step 2. Data Clean Up
df.columns = df.columns.str.strip()

# Step 3. Create/connect to a SQLite database
sqlite3.connect('instance/Database.db')

# Step 4. Load data file to SQLite
# fail;replace;append
df.to_sql('StudyGuide', con=sqlite3.connect('instance/Database.db'), if_exists='replace')

# Step 5. Close connection
sqlite3.connect('instance/Database.db').close()

