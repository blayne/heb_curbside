#!/usr/bin/env python3

from sys import exit
from time import sleep
from dateutil.parser import parse
from datetime import datetime
from getpass import getpass
import argparse
import json
import smtplib, ssl
import requests

__author__ = "Blayne Dreier"
__copyright__ = "Copyright 2020"
__credits__ = ["Blayne Dreier", "Alex Ionescu"]
__license__ = "GPL"
__version__ = "2.0"
__maintainer__ = "Blayne Dreier"
__email__ = "blayne@blaynedreier.com"
__status__ = "Production"

"""
Example:
    python find_store.py --zip 78701 --radius 25
"""

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465

def get_now():
    return datetime.now().strftime("%B %d @ %I:%M:%S %p")

class HEB:
    def __init__(self):
        self.curbside_stores = []

    @property
    def curbside_stores(self):
        return self.__curbside_stores

    @curbside_stores.setter
    def curbside_stores(self, curbside_stores):
        self.__curbside_stores = curbside_stores

    def get_curbside_stores(self, search):
        self.curbside_stores.clear()
        if search.zip:
            url = 'https://www.heb.com/commerce-api/v1/store/locator/address'
            headers = {
                "Host": "www.heb.com",
                "Content-Length": "80",
                "Content-Type": "application/json;charset=UTF-8"
            }
            payload = '{"address":"' + str(args.zip) + '","curbsideOnly":true,"radius":' + str(args.radius) + ',"nextAvailableTimeslot":true}'
            response = requests.post(url, data=payload, headers=headers)
            json_blob = json.loads(response.content)
            stores = json_blob['stores']

            for store in stores:
                curbside_store = Store(store['store']['id'])
                curbside_store.name = store['store']['name']
                curbside_store.street_address = store['store']['address1'].title()
                curbside_store.city = store['store']['city'].title()
                curbside_store.state = store['store']['state']
                curbside_store.zip = store['store']['postalCode']
                if search.detail:
                    url = 'https://www.heb.com/commerce-api/v1/cart/fulfillment/pickup'
                    payload = '{"ignoreCartChangeWarnings":false,"pickupStoreId":"'+ curbside_store.id +'"}'
                    content_length = len(payload) + 5
                    headers = {
                        "Host": "www.heb.com",
                        "Content-Length": str(content_length),
                        "Content-Type": "application/json;charset=UTF-8"
                    }
                    response = requests.post(url, data=payload, headers=headers)
                    store_blob = json.loads(response.content)
                    curbside_store.markup = store_blob['markup'][:1]

                    url = 'https://www.heb.com/commerce-api/v1/timeslot/timeslots?store_id={}&days=15&fulfillment_type=pickup'.format(curbside_store.id)
                    headers = {
                        "Host": "www.heb.com"
                    }
                    response = requests.get(url, headers=headers)
                    json_blob = json.loads(response.content)

                    timeslots = json_blob['items']
                    for timeslot in timeslots:
                        time_slot = Timeslot(timeslot['timeslot']['startTime'])
                        time_slot.price = timeslot['timeslot']['totalPrice']
                        curbside_store.timeslots.append(time_slot)
                else:
                    if len(store['storeNextAvailableTimeslot']['nextAvailableTimeslotDate']) > 0:
                        time_slot = Timeslot(store['storeNextAvailableTimeslot']['nextAvailableTimeslotDate'])
                        curbside_store.timeslots.append(time_slot)

                self.curbside_stores.append(curbside_store)
        elif search.store_id:
            url = 'https://www.heb.com/commerce-api/v1/cart/fulfillment/pickup'
            payload = '{"ignoreCartChangeWarnings":false,"pickupStoreId":"'+ str(search.store_id) +'"}'
            content_length = len(payload) + 5
            headers = {
                "Host": "www.heb.com",
                "Content-Length": str(content_length),
                "Content-Type": "application/json;charset=UTF-8"
            }
            response = requests.post(url, data=payload, headers=headers)
            store = json.loads(response.content)
            curbside_store = Store(store['store']['id'])
            curbside_store.name = store['store']['name']
            curbside_store.street_address = store['store']['address1'].title()
            curbside_store.city = store['store']['city'].title()
            curbside_store.state = store['store']['state']
            curbside_store.zip = store['store']['postalCode']
            if search.detail:
                curbside_store.markup = store['markup'][:1]

            url = 'https://www.heb.com/commerce-api/v1/timeslot/timeslots?store_id={}&days=15&fulfillment_type=pickup'.format(curbside_store.id)
            headers = {
                "Host": "www.heb.com"
            }
            response = requests.get(url, headers=headers)
            json_blob = json.loads(response.content)

            timeslots = json_blob['items']
            for timeslot in timeslots:
                time_slot = Timeslot(timeslot['timeslot']['startTime'])
                time_slot.price = timeslot['timeslot']['totalPrice']
                curbside_store.timeslots.append(time_slot)

            self.curbside_stores.append(curbside_store)


class Search:
    def __init__(self):
        self.num_curbside_slots = 0
        self.heb = HEB()

    @property
    def zip(self):
        return self.__zip

    @zip.setter
    def zip(self, zip):
        self.__zip = zip

    @property
    def radius(self):
        return self.__radius

    @radius.setter
    def radius(self, radius):
        self.__radius = radius

    @property
    def is_daemonized(self):
        return self.__is_daemonized

    @is_daemonized.setter
    def is_daemonized(self, is_daemonized):
        self.__is_daemonized = is_daemonized

    @property
    def interval(self):
        return self.__interval

    @interval.setter
    def interval(self, interval):
        self.__interval = interval

    @property
    def speak(self):
        return self.__speak

    @speak.setter
    def speak(self, speak):
        self.__speak = speak

    @property
    def detail(self):
        return self.__detail

    @detail.setter
    def detail(self, detail):
        self.__detail = detail

    @property
    def email_to(self):
        return self.__email_to

    @email_to.setter
    def email_to(self, email_to):
        self.__email_to = email_to

    @property
    def email_username(self):
        return self.__email_username

    @email_username.setter
    def email_username(self, email_username):
        self.__email_username = email_username

    @property
    def email_password(self):
        return self.__email_password

    @email_password.setter
    def email_password(self, email_password):
        self.__email_password = email_password

    @property
    def store_id(self):
        return self.__store_id

    @store_id.setter
    def store_id(self, store_id):
        self.__store_id = store_id

    @property
    def num_curbside_slots(self):
        return self.__num_curbside_slots

    @num_curbside_slots.setter
    def num_curbside_slots(self, num_curbside_slots):
        self.__num_curbside_slots = num_curbside_slots

    def print_attributes(self):
        print("zip: " + str(self.zip))
        print("radius: " + str(self.radius))
        print("store_id: " + str(self.store_id))
        print("detail: " + str(self.detail))
        print("daemon: " + str(self.daemon))
        print("interval: " + str(self.interval))
        print("speak: " + str(self.speak))
        print("email_to: " + str(self.email_to))
        print("email_username: " + str(self.email_username))

    def speak_num_curbside_slots(self):
        if self.speak:
            import mac_say
            if self.num_curbside_slots > 0:
                if self.detail or self.store_id:
                    try:
                        if self.num_curbside_slots == 1:
                            mac_say.say("One curbside slot found")
                        else:
                            mac_say.say("{} curbside slots found".format(self.num_curbside_slots))
                    except Exception as e:
                        print(e)
                else:
                    try:
                        if self.num_curbside_slots == 1:
                            mac_say.say("One store with curbside slots found")
                        else:
                            mac_say.say("{} stores with curbside slots found".format(self.num_curbside_slots))
                    except Exception as e:
                        print(e)

    def send_email(self):
        if self.email_to:
            if self.num_curbside_slots > 0:
                context = ssl.create_default_context()
                email_body = "Subject: H-E-B Curbside slots found!\n\n"
                email_body = email_body + "Stores with available Curbside (as of {}):\n\n".format(get_now())
                for curbside_store in self.heb.curbside_stores:
                    if self.slots_only and len(curbside_store.timeslots) < 1:
                        continue
                    email_body = email_body + curbside_store.get_header_text()
                    markup_text = curbside_store.get_markup_text()
                    if markup_text:
                        email_body = email_body + markup_text
                    email_body = email_body + curbside_store.get_timeslots_text()
                    email_body = email_body + "\n"
                try:
                    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
                        server.login(self.email_username, self.email_password)
                        server.sendmail(self.email_username, self.email_to, email_body)
                except Exception as e:
                    print(e)


class Store:
    def __init__(self, id):
        self.id = id
        self.timeslots = []
        self.markup = None
        self.next_available_timeslot = None

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, id):
        self.__id = id

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name

    @property
    def street_address(self):
        return self.__street_address

    @street_address.setter
    def street_address(self, street_address):
        self.__street_address = street_address

    @property
    def city(self):
        return self.__city

    @city.setter
    def city(self, city):
        self.__city = city

    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, state):
        self.__state = state

    @property
    def zip(self):
        return self.__zip

    @zip.setter
    def zip(self, zip):
        self.__zip = zip

    @property
    def markup(self):
        return self.__markup

    @markup.setter
    def markup(self, markup):
        self.__markup = markup

    @property
    def timeslots(self):
        return self.__timeslots

    @timeslots.setter
    def timeslots(self, timeslots):
        self.__timeslots = timeslots

    def get_attributes_text(self):
        attributes_text = "id: " + str(self.id)
        attributes_text = attributes_text + "name: {}\n".format(str(self.name))
        attributes_text = attributes_text + "street_address: {}\n".format(str(self.street_address))
        attributes_text = attributes_text + "city: {}\n".format(str(self.city))
        attributes_text = attributes_text + "state: {}\n".format(str(self.state))
        attributes_text = attributes_text + "zip: {}\n".format(str(self.zip))
        attributes_text = attributes_text + "markup: {}\n".format(str(self.markup))
        attributes_text = attributes_text + "next_available_timeslot: {}\n".format(str(self.next_available_timeslot))
        for timeslot in self.timeslots:
            attributes_text = attributes_text + "timeslot: {}\n".format(str(timeslot))
        return attributes_text

    def get_header_text(self):
        header_text = "{} (#{})\n".format(self.name, self.id)
        header_text = header_text + "{}, {}, {}, {}\n".format(
            self.street_address,
            self.city,
            self.state,
            self.zip)
        return header_text

    def get_timeslots_text(self):
        timeslots_text = "Available Curbside slots:\n"
        if self.timeslots:
            for timeslot in self.timeslots:
                timeslot_start_time = parse(timeslot.start_time)
                if not timeslot.price is None:
                    timeslots_text = timeslots_text + "{} for ${:,.2f}\n".format(timeslot_start_time.strftime("%B %d @ %I:%M %p"), timeslot.price)
                else:
                    timeslots_text = timeslots_text + "{}\n".format(timeslot_start_time.strftime("%B %d @ %I:%M %p"))
        else:
            timeslots_text = timeslots_text + "{} - There are no Curbside slots available.\n".format(get_now())
        return timeslots_text

    def get_markup_text(self):
        if self.markup:
            return "Curbside product markup: {}%\n".format(self.markup)
        else:
            return None


class Timeslot:
    def __init__(self, start_time):
        self.start_time = start_time
        self.price = None

    @property
    def start_time(self):
        return self.__start_time

    @start_time.setter
    def start_time(self, start_time):
        self.__start_time = start_time

    @property
    def end_time(self):
        return self.__end_time

    @end_time.setter
    def end_time(self, end_time):
        self.__end_time = end_time

    @property
    def price(self):
        return self.__price

    @price.setter
    def price(self, price):
        self.__price = price


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--zip", help="Your zip code")
    parser.add_argument(
        "--store-id",
        help="Monitor Curbside slots at a single store")
    parser.add_argument(
        "--radius",
        help="The radius to search (in miles, default=25)",
        default=25)
    parser.add_argument(
        "--detail",
        help="Show all available Curbside slots and their prices",
        action='store_true',
        default=False)
    parser.add_argument(
        "--daemon",
        help="Check Curbside availability every interval",
        action='store_true')
    parser.add_argument(
        "--slots-only",
        help="Only show stores with Curbside slots",
        action='store_true',
        default=False)
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
        "--email-username",
        help="Your Gmail username")
    args = parser.parse_args()

    if args.email_to and (args.email_username is None):
        parser.error("--email-to requires --email-username")
        exit(1)
    if (args.store_id is None and args.zip is None) or (not args.store_id is None and not args.zip is None):
        parser.print_help()
        print("\nError: Either --store_id or --zip (but not both) must be supplied.")
        exit(1)

    search = Search()
    search.zip = args.zip if args.zip else None
    search.radius = args.radius if args.radius else 25
    search.store_id = args.store_id if args.store_id else None
    search.detail = args.detail if args.detail else False
    search.daemon = args.daemon if args.daemon else False
    search.slots_only = args.slots_only if args.slots_only else False
    search.interval = args.interval * 60 if args.interval else 300
    search.speak = args.speak if args.speak else False
    search.email_to = args.email_to if args.email_to else None
    search.email_username = args.email_username if args.email_username else None
    if search.email_to:
        search.email_password = getpass(prompt="Password for {}:".format(search.email_username))
    if not search.daemon:
        search.interval = 0

    first_run = True
    while first_run or search.daemon:
        search.heb.get_curbside_stores(search)
        print("Stores with available Curbside (as of {}):\n".format(get_now()))
        for curbside_store in search.heb.curbside_stores:
            if search.slots_only and len(curbside_store.timeslots) < 1:
                continue
            output = curbside_store.get_header_text()
            markup_text = curbside_store.get_markup_text()
            if markup_text:
                output = output + markup_text
            output = output + curbside_store.get_timeslots_text()
            print(output)
        curbside_stores_timeslots = [[curbside_timeslot for curbside_timeslot in curbside_store.timeslots] for curbside_store in search.heb.curbside_stores]
        curbside_timeslots = [curbside_timeslot for curbside_store_timeslots in curbside_stores_timeslots for curbside_timeslot in curbside_store_timeslots]
        search.num_curbside_slots = len(curbside_timeslots)
        search.speak_num_curbside_slots()
        search.send_email()
        sleep(search.interval)
        first_run = False
