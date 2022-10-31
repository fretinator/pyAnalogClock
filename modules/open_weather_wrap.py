#! /usr/bin/python

import datetime
import json
from urllib import request as urllib
import sys

# proxies for testing
myProxies = {}

BASE_ICON_URL = 'http://openweathermap.org/img/wn/'

# openweathermap api key
myApiKey = "a0050fa2115ae0d6ce44dac252089f9b"
apiVer = "2.5"
defaultCityID = 4233813 # Your city
nl = "\n"
trueVal="true"
debug=trueVal

def convertDateTime(time, format='%m/%d/%Y %I:%M %p'):
    return datetime.datetime.fromtimestamp(
        int(time)
    ).strftime(format)

def convertTimeOnly(time, format='%I:%M %p'):
    return datetime.datetime.fromtimestamp(
        int(time)
    ).strftime(format)

def convertDateOnly(time, format='%m/d/%Y'):
    return datetime.datetime.fromtimestamp(
        int(time)
    ).strftime(format)

class CurrentWeather:
    city = ""
    country = ""
    temp = ""
    tempMax = ""
    tempMin = ""
    humidity = ""
    pressure = ""
    sky = ""
    description = ""
    sunrise = ""
    sunset = ""
    wind = ""
    windDir = ""
    dateTime = ""
    clouds = ""
    icon = ""

    def __init__(self, weatherDict):
        self.city = weatherDict.get('name')
        self.country = weatherDict.get('sys').get('country')
        self.temp = weatherDict.get('main').get('temp')
        self.tempMax = weatherDict.get('main').get('temp_max')
        self.tempMin = weatherDict.get('main').get('temp_min')
        self.humidity = weatherDict.get('main').get('humidity')
        self.pressure = weatherDict.get('main').get('pressure')
        self.sky = weatherDict['weather'][0]['main']
        self.description = weatherDict['weather'][0]['description']
        self.icon = weatherDict['weather'][0]['icon']
        self.sunrise = convertTimeOnly(weatherDict.get('sys').get('sunrise'))
        self.sunset = convertTimeOnly(weatherDict.get('sys').get('sunset'))
        self.wind = weatherDict.get('wind').get('speed')
        self.windDir = weatherDict.get('wind').get('deg')
        self.dateTime = convertDateTime(weatherDict.get('dt'))
        self.clouds = weatherDict.get('clouds').get('all')

    def getIconURL(self, scaling: int):
        global BASE_ICON_URL

        return BASE_ICON_URL + self.icon + str(scaling) + 'x.png'

    def dumpWeather(self):
        print("city=" + self.city)
        print("country=" + self.country)
        print("temp=" + str(self.temp))
        print("tempMax=" + str(self.tempMax))
        print("tempMin=" + str(self.tempMin))
        print("humidity=" + str(self.humidity))
        print("pressure=" + str(self.pressure))
        print("sky=" + str(self.sky))
        print("description=" + self.description)
        print("icon=" + self.icon)
        print("sunrise=" + self.sunrise)
        print("sunset=" + self.sunset)
        print("wind=" + str(self.wind))
        print("windDir=" + str(self.windDir))
        print("dateTime=" + self.dateTime)
        print("city=" + self.city)
        print("clouds=" + str(self.clouds))

def getRequestURL(cityID=defaultCityID, units="imperial") :
    apiBaseURL = 'http://api.openweathermap.org/data/' + apiVer + '/weather?id='
    apiFullUrl = apiBaseURL + str(cityID) + '&mode=json&units=' + units + '&APPID=' + myApiKey

    return apiFullUrl

def getCurrentWeatherData(cityID=defaultCityID, units="imperial"):
    apiURL = getRequestURL(cityID,units)
    url =  urllib.urlopen(apiURL)
    output = url.read().decode('utf-8')

    weatherDict = json.loads(output)
    url.close()
    weatherObj = CurrentWeather(weatherDict)
    return weatherObj

# Search for your city ID here: http://bulk.openweathermap.org/sample/city.list.json.gz
if __name__ == "__main__":
    cityID = defaultCityID
    units = "imperial"

    if len(sys.argv) > 1:
        cityID = sys.argv[1]
        if len(sys.argv > 2):
            units=argv[2]

    myWeather = getCurrentWeatherData(cityID, units)
    myWeather.dumpWeather()

