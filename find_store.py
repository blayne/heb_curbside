import requests
import json
import time
import argparse
import mac_say
import smtplib, ssl
from getpass import getpass
from dateutil.parser import parse
from datetime import datetime
from sys import exit

SMTP_PORT = 465

parser = argparse.ArgumentParser()
parser.add_argument("--zip", help="Your zip code", required=True)
parser.add_argument(
    "--radius",
    help="The radius to search (in miles)",
    required=True)
parser.add_argument(
    "--detail",
    help="Show all available Curbside slots and their prices",
    action='store_true')
parser.add_argument(
    "--daemon",
    help="Check Curbside availability every interval",
    action='store_true')
parser.add_argument(
    "--interval",
    type=int,
    help="Interval at which the daemon should check availability (in minutes, default=5)",
    default=5)
parser.add_argument(
    "--speak",
    help="Speak when a slot is found",
    action='store_true')
parser.add_argument(
    "--email-to",
    help="The address to email when slots are found")
parser.add_argument(
    "--username",
    help="Your Gmail username")
args = parser.parse_args()

if args.email_to and (args.username is None):
    parser.error("--email-to requires --username")
    sys.exit(1)

if args.email_to:
    email_password = getpass(prompt="Password for {}:".format(args.username))

def get_now():
    return datetime.now().strftime("%B %d @ %I:%M:%S %p")

def print_no_slots():
    print("{} - There are no Curbside slots available.".format(get_now()))

def find_stores():
    url = 'https://www.heb.com/commerce-api/v1/store/locator/address'
    headers = {
        "Host": "www.heb.com",
        "Content-Length": "80",
        "Content-Type": "application/json;charset=UTF-8"
    }

    payload = '{"address":"' + str(args.zip) + '","curbsideOnly":true,"radius":' + str(args.radius) + ',"nextAvailableTimeslot":true}'
    response = requests.post(url, data=payload, headers=headers)

    json_blob = json.loads(response.content)
    stores_blob = None

    if 'stores' in json_blob:
        store_blob = json_blob['stores']
        stores_available = [store for store in store_blob if store['storeNextAvailableTimeslot']['nextAvailableTimeslotDate']]
    else:
        stores_available = None

    return stores_available

def get_all_slots(stores_available):
    slots = ""
    slots = slots + "Stores with available Curbside (as of {}):\n".format(get_now())
    for store in stores_available:
        slots = slots + "\n"
        slots = slots + "{}\n".format(store['store']['name'])
        slots = slots + "{}, {}, {}, {}\n".format(
            store['store']['address1'].title(),
            store['store']['city'].title(),
            store['store']['state'],
            store['store']['postalCode'])

        url = 'https://www.heb.com/commerce-api/v1/timeslot/timeslots?store_id={}&days=15&fulfillment_type=pickup'.format(store['store']['id'])
        headers = {
            "Host": "www.heb.com"
        }
        response = requests.get(url, headers=headers)

        json_blob = json.loads(response.content)
        slots_blob = None

        if 'items' in json_blob:
            slots_blob = json_blob['items']
            slots = slots + "Available Curbside slots:\n"
            for slot_number,slot in enumerate(slots_blob):
                slot_time = parse(slot['timeslot']['startTime'])
                slots = slots + "{} for ${:,.2f}\n".format(slot_time.strftime("%B %d @ %I:%M %p"), slot['timeslot']['totalPrice'])
        else:
            slots_available = None

    return slots

def get_next_slots(stores_available):
    slots = ""
    slots = slots + "Stores with available Curbside (as of {}):\n".format(get_now())
    for store in stores_available:
        slots = slots + "\n"
        slots = slots + "{}\n".format(store['store']['name'])
        slots = slots + "{}, {}, {}, {}\n".format(
            store['store']['address1'].title(),
            store['store']['city'].title(),
            store['store']['state'],
            store['store']['postalCode'])
        available_time = parse(
            store['storeNextAvailableTimeslot']['nextAvailableTimeslotDate'])
        slots = slots + "Next available slot: {}\n".format(available_time.strftime("%B %d @ %I:%M %p"))

    return slots

def speak():
    try:
        mac_say.say("Curbside slot found")
    except Exception as e:
        print(e)

def send_email(slots):
    context = ssl.create_default_context()

    email_body = "Subject: H-E-B Curbside slots found!\n\n{}".format(slots)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", SMTP_PORT, context=context) as server:
            server.login(args.username, email_password)
            server.sendmail(args.username, args.email_to, email_body)
    except Exception as e:
        print(e)

if args.daemon:
    while True:
        stores_available = find_stores()
        if stores_available:
            if args.detail:
                slots = get_all_slots(stores_available)
            else:
                slots = get_next_slots(stores_available)
            print(slots)
            if args.speak: speak()
            if args.email_to: send_email(slots)
        else:
            print_no_slots()
        interval = args.interval * 60
        time.sleep(interval)
else:
    stores_available = find_stores()
    if stores_available:
        if args.detail:
            slots = get_all_slots(stores_available)
        else:
            slots = get_next_slots(stores_available)
        print(slots)
        get_all_slots(stores_available)
        if args.speak: speak()
        if args.email_to: send_email(slots)
    else:
        print_no_slots()
