#! /usr/bin/env python3

import re
import subprocess
import time
import sys
import sqlite3
import datetime
import RPi.GPIO as GPIO

# Raspberry pins controlling 2rt and 3rt relays
TWO_RT = 12
THREE_RT = 16


def leading_zero(nb):
    return (str(nb), '0' + str(nb))[nb < 10]

def raspberry_pin_setup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setup(TWO_RT, GPIO.OUT)
    GPIO.setup(THREE_RT, GPIO.OUT)
    GPIO.output(TWO_RT, GPIO.LOW)
    GPIO.output(THREE_RT, GPIO.LOW)

def disconnect_motherboard_from_lock():
    print('3rt click')
    GPIO.output(THREE_RT, GPIO.HIGH)
    time.sleep(0.5)

def reconnect_motherboard_to_lock():
    print('3rt click')
    GPIO.output(THREE_RT, GPIO.LOW)

def send_signal_to_lock():
    print('2rt click')
    GPIO.output(TWO_RT, GPIO.HIGH)
    time.sleep(0.5)
    print('2rt click')
    GPIO.output(TWO_RT, GPIO.LOW)
    time.sleep(0.5)

try:
    raspberry_pin_setup()

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
                    print('You must register before using this hoven')


                # ID is valid and registered
                else:
                    print('User found')
                    # Update last use DATE
                    now = datetime.datetime.now()
                    cursor.execute("UPDATE Users SET DATE = '" + str(now.day) +"/" + str(now.month) + "/" + str(now.year) + " " + str(leading_zero(now.hour)) + ":" + str(leading_zero(now.minute)) + "' WHERE ID = '" + line + "'")
                    print("Database updated")

                    disconnect_motherboard_from_lock()
                    # Send a signal to unlock the hoven
                    send_signal_to_lock()
                    print('Hoven opened')
                    # Gives 5 seconds to the user to put his shit in the hoven and close it
                    time.sleep(5)
                    # Send a signal to lock the hoven
                    send_signal_to_lock()
                    reconnect_motherboard_to_lock()
                    print('Hoven closed')



                # Commit sqlite requests
                conn.commit()
                break

# Keyboard interrupt handling
except KeyboardInterrupt:
        GPIO.output(TWO_RT, GPIO.LOW)
        GPIO.output(THREE_RT, GPIO.LOW)
        GPIO.cleanup()
        conn.close()
