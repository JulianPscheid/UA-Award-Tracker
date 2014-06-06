# Alaska Award Search script
# Date: May 18, 2014
# Author: @julianpscheid

import os
from flask import Flask
import sys
import mechanize
from bs4 import BeautifulSoup
import requests
from parse_rest.connection import register
from parse_rest.datatypes import Object
import datetime


# Email function
def send_message(messageTitle, notificationMessage):
    return requests.post(
        "https://api.mailgun.net/v2/mg.pscheid.com/messages",
        auth=("api", "key-3wsmng64q81hxvk6fg8crfe9yeaz4-v8"),
        data={"from": "Alaska Award Alert <alerts@mg.pscheid.com>",
              "to": ["julian@pscheid.com"],
              "subject": "Alaska Award Alert: " + messageTitle,
              "text": notificationMessage})

def runSearch(departureLocation, destinationLocation, departureDate, numberAdults, alertOnEconomy, alertOnBusiness, alertOnFirst):
    # Tweak the dates
    returnDate = datetime.date.today() + datetime.timedelta(days=330)
    departureDateString = departureDate.strftime('%m/%d/%Y')
    returnDateString = returnDate.strftime('%m/%d/%Y')

    # Configuration
    br = mechanize.Browser()
    br.set_handle_robots(False)   # ignore robots
    br.set_handle_refresh(False)  # can sometimes hang without this
    br.addheaders = [('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36')]

    # Load the form page on United.com
    br.open("http://www.alaskaair.com/planbook?lid=nav:planbook-flights")
    br.select_form(nr=1)
    br['ShoppingRequestModel.DepartureCity1'] = departureLocation
    br['ShoppingRequestModel.ArrivalCity1'] = destinationLocation
    br['ShoppingRequestModel.DepartureDate1'] = departureDateString
    br['ShoppingRequestModel.ReturnDate'] = returnDateString
    br.form['ShoppingRequestModel.AwardOption'] = ["MilesOnly"]
    numberAdultsList = []
    numberAdultsList.append(numberAdults)
    br.form['ShoppingRequestModel.AdultCount'] = numberAdultsList
    response = br.submit('findFlights')

    # email content
    messageTitle = departureLocation + " to " + destinationLocation + " on " + departureDateString + " for " + numberAdults + " adult(s)"
    notificationMessage = "Search: from " + messageTitle + "\n\n"
    print notificationMessage

    # Parse the results
    soup = BeautifulSoup(response.get_data())
    print soup
    '''
    parent_table = soup.find('table', {"class" : "rewardResults"})
    records = []
    globalResultsEconomy = False
    globalResultsBusiness = False
    globalResultsFirst = False
    for row in parent_table.findAll('tr', recursive=False):
        col = row.findAll('td', recursive=False) 
        currentResults = False
        currentResultsEconomy = False
        currentResultsBusiness = False
        currentResultsFirst = False
        if len(col)>5:
            if alertOnEconomy and len(col[0].findAll('div', {"class" : "divNA"})) == 0:
                # SAVER ECONOMY
                currentResults = True
                currentResultsEconomy = True
                globalResultsEconomy = True
            if alertOnBusiness and len(col[2].findAll('div', {"class" : "divNA"})) == 0:
                #SAVER BUSINESS
                currentResults = True
                currentResultsBusiness = True
                globalResultsBusiness = True
            if alertOnFirst and len(col[4].findAll('div', {"class" : "divNA"})) == 0:
                #SAVER FIRST
                currentResults = True
                currentResultsFirst = True
                globalResultsFirst = True
            if currentResults == True:
                print "\n---------------- NEW FLIGHT WITH SAVER AVAILABILITY------------------"
                notificationMessage += "\n---------------- NEW FLIGHT WITH SAVER AVAILABILITY------------------\n"
                if currentResultsEconomy:
                    print "ECONOMY"
                    notificationMessage += "ECONOMY\n"
                if currentResultsBusiness:
                    print "BUSINESS"
                    notificationMessage += "BUSINESS\n"
                if currentResultsFirst:
                    print "FIRST"
                    notificationMessage += "FIRST\n"
                flightArray = col[6].findAll('td', {"class" : "tdDepart"})
                for flight in flightArray:
                    print list(flight.next_siblings)[5].contents[1].get_text()
                    print flight.get_text(" ", strip=True)
                    print list(flight.next_siblings)[3].get_text(" ", strip=True)
                    notificationMessage += (list(flight.next_siblings)[5].contents[1].get_text() + "\n")
                    notificationMessage += (flight.get_text(" ", strip=True) + "\n")
                    notificationMessage += (list(flight.next_siblings)[3].get_text(" ", strip=True) + "\n")

    if globalResultsEconomy:
        print "Results contain Economy class options"
    if globalResultsBusiness:
        print "Results contain Business class options"
    if globalResultsFirst:
        print "Results contain First class options"
    if globalResultsEconomy or globalResultsBusiness or globalResultsFirst:
        # Trigger the function that sends the email
        print ""
        send_message(messageTitle, notificationMessage)
    if not globalResultsEconomy and not globalResultsBusiness and not globalResultsFirst:
        print "No Saver Award availability"
    '''

app = Flask(__name__)

@app.route('/')

def alaska_search():
    # check to make sure this only runs at certain times during the day. Heroku servers are UTC (+7)
    currentHour = datetime.datetime.now().hour - 7
    awardCount = 0
    if True: # (currentHour == 6 or currentHour == 10 or currentHour == 14 or currentHour == 18 or currentHour == 21):
        print "It is " + str(currentHour) + " o'clock at home. Running this script!"
        # configure Parse and query for searches
        register("SpnGvUWutUhTbMGV9wCuzvfzzFsLRQLsRXzXwA35", "2Jj1pEDncRdD3lTYxfgqApkPKLhzMKQb0nHnV7Oa")
        class awardSearch(Object):
            pass
        allAwardSearches = awardSearch.Query.all()
        for awardSearch in allAwardSearches:
            runSearch(awardSearch.departureLocation, awardSearch.destinationLocation, awardSearch.departureDate, str(awardSearch.numberAdults), awardSearch.alertOnEconomy, awardSearch.alertOnBusiness, awardSearch.alertOnFirst)
            awardCount+=1
        send_message("Search task completed", "The task ran and completed "+str(awardCount)+" searches.")

alaska_search()