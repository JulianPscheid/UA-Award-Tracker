UA-Award-Tracker
================

Python application that scans the UA website for award availability and sends out notification emails based on results.

Packages used:

Mechanize
---------
The application uses Mechanize to create a session on United.com and submit the forms.

BeautifulSoup
-------------
Used to parse the results page.

Parse
-----
I use Parse.com to store a database of all the searches that I'm running. This allows me to easily add and remove searches without needing to edit the application. The table I use is set up the following way:

```sh
{ "results": [
	{
        "alertOnBusiness": true,
        "alertOnEconomy": false,
        "alertOnFirst": true,
        "createdAt": "2014-05-18T16:47:33.767Z",
        "departureDate": {
            "__type": "Date",
            "iso": "2014-12-15T16:47:00.000Z"
        },
        "departureLocation": "sfo",
        "destinationLocation": "fra",
        "numberAdults": 2,
        "objectId": "35XWHOC9xo",
        "updatedAt": "2014-05-18T16:47:59.319Z"
    }
] }
```
The API key is XXX'ed out, so feel free to hardcode your search for now if you don't want to set up a Parse account.


Mailgun
-------
Mailgun is used to send results notifications.


Hosting
-------
I run this application on Heroku within a free account. I use the Heroku scheduler to run the search hourly, although you'll see that I limit it to actually hitting United.com only 5 times a day.
