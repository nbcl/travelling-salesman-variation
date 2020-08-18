from random import uniform, randrange, randint
from shapely.geometry import Point, Polygon
from router import YROUTER as yroute

# DEFINED PARAMETERS
BIG_M = 1000000

# Velocity
VELOCITY = 1

# Max omo demand
OMO_DEMAND = 4

# Max quix demand
QUIX_DEMAND = 5

# Max quix demand
MAX_QUIX = 40

# Max omo demand
MAX_OMO  = 40 

# Sector of choice
MACUL = Polygon([
    (-70.613836, -33.508178), 
    (-70.5885897, -33.5099778), 
    (-70.5805187, -33.4880171), 
    (-70.5771733, -33.4700771), 
    (-70.5880938, -33.4744469),
    (-70.6230181, -33.4750283), 
    (-70.613836, -33.508178)
])

# Days in week
WORKABLE_DAYS = 5

# Periods
PERIODS = 4

# Houses Per Period
HOUSES_PER_PERIOD = 25

# Max ammount of houses per day
HOUSES_PER_DAY = HOUSES_PER_PERIOD * PERIODS

# Total houses
TOTAL_HOUSES = HOUSES_PER_DAY * WORKABLE_DAYS

# Dart algo generates house inside multipolygon
# Adapted from original, Damian Michal Harasymczuk
# Search: "dmh126 multipolygon random"
def dart(multipolygon):
    xmin, ymin, xmax, ymax = multipolygon.bounds
    while True:
        p = Point(uniform(xmin, xmax), uniform(ymin, ymax))
        if multipolygon.contains(p):
            break
    return [p.x, p.y]

# Provides random coord house for _Ngen
def _ngen():
    return {'coords' : dart(MACUL)}

# Generates Algramo Storage Facility as House 0 in each period
def _Ngen():
    _N = []
    for i in range(HOUSES_PER_DAY * WORKABLE_DAYS):
        _N.append(_ngen())
    counter = 0
    for casa in _N:
        if counter == 0:
            casa['coords'] = [-70.6678947, -33.4916677]
            counter+=1
        if counter == HOUSES_PER_PERIOD:
            counter = 0
        else:
            counter+=1
    return _N

# Generates distances for API
def distances(_Ngen):
    distances = []
    for i in range(len(_Ngen)):
        print('Parsing route for i=' + str(i))
        eachhouse = []
        for j in range(len(_Ngen)):
            b = yroute([_Ngen[i]['coords'][0], _Ngen[i]['coords'][1]], [_Ngen[i]['coords'][0], _Ngen[j]['coords'][1]]) 
            eachhouse.append(b.drop())
        distances.append(eachhouse)
    return distances

# Generates demand
def week(_Ngen):
    week = []
    counter = 0
    for i in range(WORKABLE_DAYS):
        day = []
        for i in range(PERIODS):            
            period = []
            for i in range(HOUSES_PER_PERIOD):
                x = randrange(2)
                y = 1
                if x!=0:
                    y = randrange(2)
                pedidos = [x, y]
                b = randrange(2)
                quix = randint(0,MAX_QUIX) * pedidos[b]
                pedidos.pop(b)
                omo = randint(0, MAX_OMO) * pedidos[0]

                house = _Ngen[counter]
                house['Wjpt'] = quix
                house['Ujpt'] = omo

                period.append(house)
                counter+=1
            day.append(period)
        week.append(day)
    f = open("data/dataset.txt", "a")
    f.write(str(week))
    f.close()
    return week

# Generates distances for Eucladian formula
def new_distances(week):
    distances = []
    for t in week:
        day = []
        for p in t:
            period = []
            for i in range(len(p)):
                eachhouse = []
                for j in range(len(p)):
                    b = yroute([p[i]['coords'][0], p[i]['coords'][1]], [p[i]['coords'][0], p[j]['coords'][1]]) 
                    eachhouse.append(float(b.drop()))
                period.append(eachhouse)
            day.append(period)
        distances.append(day)
    f = open("data/distances.txt", "a")
    f.write(str(distances))
    f.close()
    return distances

NMAIN_GEN = _Ngen()
DATASET_GEN = week(NMAIN_GEN)
DIJ_PARAM_GEN = new_distances(DATASET_GEN)