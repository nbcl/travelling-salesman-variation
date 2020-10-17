import ast
import os  
import math
import requests

# Eucladian generation of distances
class YROUTER:
    def __init__ (self, COORD1, COORD2):
        self.x1 = COORD1[0]
        self.y1 = COORD1[1]
        self.x2 = COORD2[0]
        self.y2 = COORD2[1]
        self.DISTANCE = round(math.sqrt((self.x2 - self.x1)**2 + (self.y2 - self.y1)**2) * 100, 3) + 3

    def drop(self):
        return self.DISTANCE

# Api call for realistic distances
class XROUTER:

    def __init__ (self, COORD1, COORD2):
        self.URL      = 'https://api.mapbox.com/'
        self.GET      = 'directions/v5/mapbox/'
        self.TYPE     = 'driving/'
        self.COORD1   =  str(COORD1[0]) + ', ' + str(COORD1[1])
        self.COORD2   =  str(COORD2[0]) + ', ' + str(COORD2[1])
        self.ADD      = ';'
        self.SPECS    = '?radiuses=100;100'
        self.ATK      = '&access_token=pk. ADD YOUR TOKEN HERE'

        self.i()
        self.parse()

    def i(self):
        self.r = requests.get(self.URL + self.GET + self.TYPE + self.COORD1 + self.ADD + self.COORD2 + self.SPECS  + self.ATK)

    def parse(self):
        FIRST = ast.literal_eval(self.r.text)
        SECOND = ast.literal_eval(str(FIRST['routes'])[1:-1])
        THIRD = ast.literal_eval(str(SECOND['distance']))
        self.DISTANCE = THIRD/1000
    
    def drop(self):
        return round(self.DISTANCE, 2)