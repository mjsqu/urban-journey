import sqlite3
import csv
import os
import zipfile
import requests

TEXT_FILE_LIST = ['routes.txt','shapes.txt','trips.txt']

# Create a table for each text file so that we can do SQL type analysis on the data
url = "https://static.opendata.metlink.org.nz/v1/gtfs/full.zip"
path_to_zip_file = '../metlink-app/static/full.zip'
directory_to_extract_to = '../metlink-app/static'

# Get the file
r = requests.get(url)
open(path_to_zip_file , 'wb').write(r.content)

# Unzip the file
with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
    zip_ref.extractall(directory_to_extract_to)

# build a list of text files
textfiles = [file for file in os.listdir(directory_to_extract_to) if file[-3:] == 'txt']

# filter text files on those required
textfiles = [textfile for textfile in textfiles if textfile in TEXT_FILE_LIST]

print(textfiles)

def create_table(textfile):
    tablename = textfile.split('/')[-1].split('.')[0]
    con = sqlite3.connect("../metlink-app/static/gtfs.db") # change to 'sqlite:///your_filename.db'
    cur = con.cursor()

    with open(textfile,'r') as fin: # `with` statement available in 2.5+
        # csv.DictReader uses first line in file for column headings by default
        dr = csv.DictReader(fin) # comma is default delimiter
        to_db = []
        for i,row in enumerate(dr):
            number_of_columns = len(row.keys())
            
            if i == 0:
                column_list = ','.join(list(row.keys()))
                create_table_statement = f"CREATE TABLE {tablename} ({column_list});" # use your column names here
                try:
                    cur.execute(create_table_statement)
                except sqlite3.OperationalError:
                    cur.execute(f"DROP TABLE {tablename}")
                    cur.execute(create_table_statement)
            
            rowtuple = tuple([v for k,v in row.items()])
            to_db.append(rowtuple)
            
    values_placeholders = ','.join(['?' for i in range(number_of_columns)])
    insert_into_statement = f"INSERT INTO {tablename} ({column_list}) VALUES ({values_placeholders});"
    print(f"{insert_into_statement=}")
    cur.executemany(insert_into_statement, to_db)
    con.commit()
    con.close()
    
 
for t in textfiles:
    full_path = f"../metlink-app/static/{t}"
    create_table(full_path)