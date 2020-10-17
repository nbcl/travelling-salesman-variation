import time
import os
from model import route_me_for

from datasets import WORKABLE_DAYS, PERIODS, TOTAL_HOUSES, QUIX_DEMAND, OMO_DEMAND, VELOCITY, HOUSES_PER_DAY, HOUSES_PER_PERIOD, BIG_M 
from datasets import DIJ_PARAM_GEN 
from datasets import DATASET_GEN 

sols  = []
objs  = []
calls = []
lazys = []
daycount = 0
result_id = 0

for t in DATASET_GEN:
    periodcount = 0
    _P = t
    for p in _P:
        route = route_me_for(WORKABLE_DAYS, PERIODS, TOTAL_HOUSES, DIJ_PARAM_GEN[daycount][periodcount], QUIX_DEMAND, OMO_DEMAND, VELOCITY, [[p]], HOUSES_PER_DAY, HOUSES_PER_PERIOD, BIG_M, result_id)
        sol   = route.drop_callback()
        sols.append(sol)
        obj   = route.drop_obj()
        objs.append(obj)
        call = route.drop_callbacks()
        calls.append(call)
        lazy = route.drop_lazy()
        lazys.append(lazy)
        periodcount += 1
        result_id += 1
    daycount += 1

daycount = 0
result_id = 0
for t in DATASET_GEN:
    periodcount = 0
    _P = t
    for p in _P:
        print(' ')
        shout('################## [ Periodo: ' + str(periodcount) + ', Dia: ' + str(daycount) + '. ] ##################')
        shout('#                                                           ')
        shout('# ✔️ La distancia optimizada es de :' + str(objs[result_id]) + ' km.                '  )
        shout('# ✔️ El camino a seguir es : ' + str(sols[result_id])+ '.  '  )
        if calls[result_id] >= 10:
            shout('# ✔️ La cantidad de callbacks realizados es : ' + str(calls[result_id])  + '.            ')
        else: 
            shout('# ✔️ La cantidad de callbacks realizados es : ' + str(calls[result_id])  + '.             ')
        if lazys[result_id] >= 10:
            shout('# ✔️ La cantidad de restricciones flojas agregadas : ' + str(lazys[result_id])  + '.     ')
        else:
            shout('# ✔️ La cantidad de restricciones flojas agregadas : ' + str(lazys[result_id])  + '.      ')
        shout('#                                                            ')
        shout('#############################################################')
        result_id += 1
        periodcount += 1
    daycount += 1