#!/usr/bin/env python3

import sys
import sqlite3
import argparse
import datetime

conn = sqlite3.connect('/home/pi/nfc_reader/users.db')
cursor = conn.cursor()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='XOR')
    parser.add_argument('filename', type=str, help='filename')
    try:
        args = parser.parse_args()
    except:
        exit(84)

    cursor.execute("DROP TABLE IF EXISTS Users")
    cursor.execute("CREATE TABLE IF NOT EXISTS Users (ID INT NOT NULL, NAME TEXT NOT NULL, PROMO INT NOT NULL, DATE TEXT NOT NULL)")
    now = datetime.datetime.now()
    with open(args.filename, 'r') as my_file:
        id = 0
        for line in my_file:
            if id > 0:
                data = line.split(';')
                studentname = data[1]
                promofullname = data[5].split()
                promonumber = promofullname[1][0]
                cursor.execute("INSERT INTO Users (ID, NAME, PROMO, DATE) VALUES (" + str(id) + ", '" + studentname + "', '" + promonumber + "', '" + str(now.day) +"/" + str(now.month) + "/" + str(now.year) + " " + str(now.hour) + ":" + str(now.minute) + "')")
            id += 1
    conn.commit()
    conn.close()
