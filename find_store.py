import requests
import json
from dateutil.parser import parse
from datetime import datetime
import argparse
from sys import exit

parser = argparse.ArgumentParser()
parser.add_argument("--zip", help="Your zip code", required=True)
parser.add_argument("--radius", help="The radius for your search (in miles)", required=True)
args = parser.parse_args()

url = 'https://www.heb.com/commerce-api/v1/store/locator/address'
headers = {
    "Host": "www.heb.com",
    "Content-Length": "80",
    "Content-Type": "application/json;charset=UTF-8"
}

payload = '{"address":"' + str(args.zip) + '","curbsideOnly":true,"radius":' + str(args.radius) + ',"nextAvailableTimeslot":true}'
response = requests.post(url, data=payload, headers=headers)

store_blob = json.loads(response.content)['stores']
stores_available = [store for store in store_blob if store['storeNextAvailableTimeslot']['nextAvailableTimeslotDate']]

if not stores_available:
    print("There are no curbside slots available.")
    exit(1)

print("\nStores with available curbside:\n")
for store in stores_available:
    print(store['store']['name'])
    print("{}, {}, {}, {}".format(
        store['store']['address1'].title(),
        store['store']['city'].title(),
        store['store']['state'],
        store['store']['postalCode']))
    available_time = parse(store['storeNextAvailableTimeslot']['nextAvailableTimeslotDate'])
    print("Available slot: " + available_time.strftime("%B %d @ %I:%M %p"))
    print()
