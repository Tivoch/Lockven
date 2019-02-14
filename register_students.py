#! /usr/bin/env python3

import re
import subprocess
import time
import sys
import sqlite3
import datetime

def leading_zero(nb):
    return (str(nb), '0' + str(nb))[nb < 10]

try:
    # Sqlite3 setup & connection
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    while True:
        # Execute nfc-list -> reading nfc card informations
        p = subprocess.Popen("nfc-list", stdout=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()

        # Read 
        res = output.decode("utf-8")
        result = res.split("\n")
        for line in result:
            line = line.strip()
            if line.startswith('UID'):  # Get the ID line
                # parse the ID line
                line = re.sub(' +', '', line)
                line = re.sub('.*:', '', line)

                # Check if card ID is registered
                cursor.execute("SELECT * FROM Users WHERE ID = '" + line + "'")
                data = cursor.fetchall()

                # ID is unknown/invalid
                if len(data) == 0:
                    print('ID not Found')
                    name = input("Enter your Epitech id (firstname.lastname@epitech.eu):")
                    # Handle simple sql injection
                    if ';' in name:
                        print("Nice try, please be serious and rescan your card")
                        continue
                    # Verify user input
                    cursor.execute("SELECT * FROM Users WHERE NAME = '" + name + "'")
                    data = cursor.fetchall()
                    # User name not recognized in the database
                    if len(data) == 0:
                        print("Invalid Epitech id, please rescan your card")
                        continue
                    now = datetime.datetime.now()
                    cursor.execute("UPDATE Users SET ID = '" + line + "' WHERE NAME = '" + name + "'")
                    print("User successfully registered")

                # ID is valid and registered
                else:
                    print('User already registered')

                # Commit sqlite requests
                conn.commit()
                break

# Keyboard interrupt handling
except KeyboardInterrupt:
        conn.close()