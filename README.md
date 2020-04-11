# H-E-B Curbside availability finder

1. Download the program from this URL:  
https://github.com/blayne/heb_curbside/raw/first-commit/find_store

2. Open Terminal

3. Run the command below:  
`chmod +x ~/Downloads/find_store`

4. Run find_store:  
`~/Downloads/./find_store --zip 78701 --radius 25`

**With all of the options:**  
`~/Downloads/./find_store --zip 78701 --radius 25 --daemon --interval 5 --speak --email-to blayne@blaynedreier.com --username blayne.dreier@gmail.com`

## Help
```
# ~/Downloads/./find_store --help

usage: find_store.py [-h] --zip ZIP --radius RADIUS [--daemon]
                     [--interval INTERVAL] [--speak] [--email-to EMAIL_TO]
                     [--username USERNAME]

optional arguments:
  -h, --help           show this help message and exit
  --zip ZIP            Your zip code
  --radius RADIUS      The radius for your search (in miles)
  --daemon             Check curbside availability every 15 minutes
  --interval INTERVAL  Interval at which the daemon should check availability
                       (default 5 mins)
  --speak              Speak when a slot is found
  --email-to EMAIL_TO  The address to email when slots are found
  --username USERNAME  Your Gmail username
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
There are no curbside slots available.
```

## When there are slots available, you should see:
```
Stores with available curbside:

Hancock Center H-E-B
1000 East 41 St., Austin, TX, 78751-4810
Available slot: April 17 @ 07:30 PM

Mueller H-E-B
1801 E.51St Street, Austin, TX, 78723-3014
Available slot: April 18 @ 09:30 PM

```

## Docker Usage
```
$ docker build -t heb-curbside .
$ docker run heb-curbside --zip ZIP --radius RADIUS
```
