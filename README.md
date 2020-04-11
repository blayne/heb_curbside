# H-E-B Curbside availability finder

1. Download the program from this URL:  
https://github.com/blayne/heb_curbside/raw/first-commit/find_store

2. Open Terminal

3. Run the command below:  
`chmod +x ~/Downloads/find_store`

4. Run find_store:  
`~/Downloads/./find_store --zip 78701 --radius 25`

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
