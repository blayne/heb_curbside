# H-E-B Curbside availability finder

## Running the program on MacOS

1. Download the program from this URL:  
https://github.com/blayne/heb_curbside/raw/master/find_store

2. Open Terminal

3. Run the command below:  
`chmod +x ~/Downloads/find_store`

4. Run find_store:  
`~/Downloads/./find_store --zip 78701 --radius 25`

**Show all of the available options:**  
`~/Downloads/./find_store --help`

## Running the Python script

The `find_store` binary above was compiled on MacOS from `find_store.py` with `pyinstaller`. You can alternatively run `find_store.py` directly by using following commands.
```
pip3 install -r requirements.txt
python3 find_store.py --zip 78701 --radius 25
```

## Help
```
# ~/Downloads/./find_store --help

usage: find_store.py [-h] [--zip ZIP] [--store-id STORE_ID] [--radius RADIUS]
                     [--detail] [--daemon] [--slots-only]
                     [--interval INTERVAL] [--speak] [--email-to EMAIL_TO]
                     [--email-username EMAIL_USERNAME]

optional arguments:
  -h, --help            show this help message and exit
  --zip ZIP             Your zip code
  --store-id STORE_ID   Check Curbside slots at a single store
  --radius RADIUS       The radius to search (in miles, default=25)
  --detail              Show all available Curbside slots and their prices
  --daemon              Check Curbside availability every interval
  --slots-only          Only show stores with Curbside slots
  --interval INTERVAL   Interval at which the daemon should check availability
                        (in minutes, default=5)
  --speak               Speak when a slot is found
  --email-to EMAIL_TO   The address to email when slots are found
  --email-username EMAIL_USERNAME
                        Your Gmail username
  --clear-console       Clear the console before printing results, useful for
                        dashboard display in daemon mode  
```

## Gmail Authentication

If `find_store` fails to authenticate to Gmail, follow the instructions at the link below:  
https://support.google.com/mail/answer/7126229#cantsignin

## Sending a text message

To send a text message when Curbside slots are found, use the email
address syntax for your carrier from the document at the link below:  
https://www.digitaltrends.com/mobile/how-to-send-a-text-from-your-email-account/

## When there are no slots available, you should see:
```
April 11 @ 11:11:41 AM - There are no Curbside slots available.
```

## When there are slots available, you should see:
```
Stores with available Curbside (as of April 11 @ 11:13:22 AM):

Hancock Center H-E-B
1000 East 41 St., Austin, TX, 78751-4810
Available slot: April 17 @ 07:30 PM

Mueller H-E-B
1801 E.51St Street, Austin, TX, 78723-3014
Available slot: April 18 @ 09:30 PM

```

**With `--detail`**:
```
Stores with available Curbside (as of April 11 @ 06:22:20 PM):

Riverside H-E-B plus!
2508 East Riverside Drive, Austin, TX, 78741-3037
Curbside product markup: 3%
Available Curbside slots:
April 18 @ 03:00 PM for $0.00
April 18 @ 04:30 PM for $0.00
April 18 @ 06:00 PM for $0.00
April 18 @ 06:30 PM for $0.00
April 18 @ 07:00 PM for $0.00
April 18 @ 07:30 PM for $0.00
```

## Docker Usage
```
$ docker build -t heb-curbside .
$ docker run heb-curbside --zip ZIP --radius RADIUS
```
