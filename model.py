from gurobipy import GRB, Model, quicksum, tuplelist
from itertools import combinations

# subtour Function gets min(cycle) in TupleList input "edges"
# Original from https://www.gurobi.com/documentation/9.0/examples/tsp_py.html
def subtour(edges):
    global houses_per_period
    n = houses_per_period
    unvisited = list(range(n))
    cycle = range(n+1) 
    while unvisited:
        thiscycle = []
        neighbors = unvisited
        while neighbors:
            current = neighbors[0]
            thiscycle.append(current)
            unvisited.remove(current)
            neighbors = [j for i, j in edges.select(current, '*') if j in unvisited]
        if len(cycle) > len(thiscycle):
            cycle = thiscycle
    return cycle

#route_me_for class that optimizes route for <parameters> under <constraints>
class route_me_for():
    def __init__(self, WORKABLE_DAYS, PERIODS, TOTAL_HOUSES, DIJ_PARAM, 
                       QUIX_DEMAND, OMO_DEMAND, VELOCITY, DATASET, 
                       HOUSES_PER_DAY, HOUSES_PER_PERIOD, BIG_M, RESULT_ID):
        self.WORKABLE_DAYS     = 1
        self.PERIODS           = 1
        self.TOTAL_HOUSES      = TOTAL_HOUSES
        self._Dij              = DIJ_PARAM
        self.QUIX_DEMAND       = QUIX_DEMAND
        self.OMO_DEMAND        = OMO_DEMAND
        self.VELOCITY          = VELOCITY
        self.DATASET           = DATASET
        self.HOUSES_PER_DAY    = HOUSES_PER_DAY
        self.HOUSES_PER_PERIOD = HOUSES_PER_PERIOD
        self.result_id         = RESULT_ID
        self._M                = BIG_M
        self.set_model()
        self.result_helper() 
        self.set_setter()
        self.set_parameters()
        self.set_variables()
        self.get_x()
        self.set_constraints()
        self.set_var_relations()
        self.set_optimize()
        self.fix_sub()

    # Defines model
    def set_model(self):
        self.m = Model()

    # Makes getting the final result simpler
    def result_helper(self):
        global lazy_glob, callbacks_glob, houses_per_period
        houses_per_period = self.HOUSES_PER_PERIOD
        lazy_glob = 0
        callbacks_glob = 0

    # Sets Sets
    def set_setter(self):
        # Refer to: N
        self._N = list(range(0, self.HOUSES_PER_PERIOD))
        # Refer to: T
        self._T = list(range(0, self.WORKABLE_DAYS))
        # Refer to: P
        self._P = list(range(0, self.PERIODS))
        # Refer to: N/a 
        # Type: Python List of List of Lists of Dictionaries imported from datasets 
        # Description: Represents each house as a dictionary with its attributes as keys
        self._C = self.DATASET

    # Refer to: Wjpt 
    def _Wjpt(self, j,p,t):
        return self._C[t][p][j]['Wjpt']
    
    # Refer to: Ujpt
    def _Ujpt(self, j,p,t):
        return self._C[t][p][j]['Ujpt']

    # Sets Parameters
    def set_parameters(self):
        # Refer to: N/a
        # Type: Python int
        # Description: Defines how many houses are expected to be in a day
        self._H = self.HOUSES_PER_DAY
        # Refer to: N/a
        # Type: Python int
        # Description: Defines how many houses are expected to be in a period
        self._G = self.HOUSES_PER_PERIOD 
        # Refer to: fp
        self._fp = 60
        # Refer to: V 
        self._V = self.VELOCITY
        # Refer to: a
        self._a = self.OMO_DEMAND
        # Refer to: b
        self._b = self.QUIX_DEMAND

    # Sets variables
    def set_variables(self):
        # Refer to: Xijpt  
        self._Xijpt = self.m.addVars(self._N, self._N, self._P, self._T, vtype=GRB.BINARY, name='Xijpt') 
        # Refer to: Ajpt 
        self._Ajpt = self.m.addVars(self._N, self._P, self._T, lb=0, vtype=GRB.INTEGER, name='Ajpt')  
        # Refer to: Bjpt 
        self._Bjpt = self.m.addVars(self._N, self._P, self._T, lb=0, vtype=GRB.INTEGER, name='Bjpt') 
        # Refer to: Zjpt 
        self._Zjpt = self.m.addVars(self._N, self._P, self._T, vtype=GRB.BINARY, name='Zijpt') 
        # Refer to: Ojpt 
        self._Ojpt = self.m.addVars(self._N, self._P, self._T, vtype=GRB.BINARY, name='Ojpt') 
        # Refer to: Qjpt 
        self._Qjpt = self.m.addVars(self._N, self._P, self._T, vtype=GRB.BINARY, name='Qjpt') 
        # Refer to: Hjpt 
        self._Hjpt = self.m.addVars(self._N, self._P, self._T, lb=0, vtype=GRB.INTEGER, name='Hjpt')

    # Sets constraints
    def set_constraints(self):
        # Refer to: 1. Unique exit 
        for i in self._N:
            self.m.addConstr(sum(self._Xijpt[i, j, p, t] for j in self._N for t in self._T for p in self._P if i != j) == 1)
        # Refer to: 2. Unique entry 
        for j in self._N:
            self.m.addConstr(sum(self._Xijpt[i, j, p, t] for t in self._T for p in self._P for i in self._N if j != i) == 1)
        # 3. Max houses in a day cannot be more than max house ammount
        for t in self._T:
            self.m.addConstr(sum(self._Xijpt[i, j, p, t] for p in self._P for i in self._N for j in self._N if j != i) <= self._H)
        # 4. Max houses in a period cannot be more than max house ammount
        for t in self._T:
            for p in self._P:
                self.m.addConstr(sum(self._Xijpt[i, j, p, t] for i in self._N for j in self._N if j != i) <= self._G)

        # 5. i,j House route must belong to set day
        # Includes a pythonian fix
        dia_aux = [self._N[x:x + self.HOUSES_PER_DAY] for x in range(0, len(self._N), self.HOUSES_PER_DAY)]
        for t in self._T:
            for p in self._P:
                for i in self._N:
                    for j in self._N:
                        if i not in dia_aux[t]:
                            self.m.addConstr(self._Xijpt[i, j, p, t] == 0)
                            
                        if j not in dia_aux[t]:
                            self.m.addConstr(self._Xijpt[i, j, p, t] == 0)

        # 6. i,j House route must belong to set period
        # Includes a pythonian fix
        period_aux = [self._N[x:x + self.PERIODS] for x in range(0, len(self._N), self.PERIODS)]
        counter = 0
        for day in period_aux:
            for i in range(len(day)):
                day[i] = counter
            if counter == self.PERIODS-1:
                counter = 0
            else:
                counter+=1

        periods = []
        for sublist in period_aux:
            for element in sublist:
                periods.append(element)

        for t in self._T:
            for p in self._P:
                for i in self._N:
                    for j in self._N:
                        if periods[i] != p:
                            self.m.addConstr(self._Xijpt[i, j, p, t] == 0)
                        if periods[j] != p:
                            self.m.addConstr(self._Xijpt[i, j, p, t] == 0)
        # 11. Las siguientes 8 restricciones fueron las agregadas por fotografias
        for t in self._T:
            for p in self._P:
                for j in self._N[:-1]:
                    self.m.addConstr(self._Bjpt[j+1, p, t] == self._Bjpt[j, p, t] - self._Wjpt(j, p, t))

        for t in self._T:
            for p in self._P:
                for j in self._N[:-1]:
                    self.m.addConstr(self._Ajpt[j+1, p, t] == self._Ajpt[j, p, t] - self._Ujpt(j, p, t))


        for t in self._T:
            for p in self._P:
                for j in self._N:
                    self.m.addConstr(self._Ojpt[j, p, t] * self._Ujpt(j, p, t) <= self._Ajpt[j, p, t])

        for t in self._T:
            for p in self._P:
                for j in self._N:
                    self.m.addConstr(self._Qjpt[j, p, t] * self._Wjpt(j, p, t) <= self._Bjpt[j, p, t])
    # Sets variable relations
    def set_var_relations(self):
        # 8.1 Omo binary under request binary
        for t in self._T:
            for p in self._P:
                for j in self._N:
                    self.m.addConstr(self._Zjpt[j, p, t] <= self._Ojpt[j,p,t] + self._Qjpt[j,p,t])
        # 8.2 Quix binary under request binary
        for t in self._T:
            for p in self._P:
                for j in self._N:
                    self.m.addConstr((self._Qjpt[j, p, t] + self._Ojpt[j,p,t]) <= self._Zjpt[j, p, t] * 2)
        # 8.3 Trace binary summation?
        for t in self._T:
            for p in self._P:
                for j in self._N:
                    #if i != j: 
                    # $COMMENT If statement not recognizing i? changed to addConstr function
                    self.m.addConstr(sum(self._Xijpt[i, j, p, t] for i in self._N if i != j) == self._Zjpt[j, p, t])
        # 8.5 Request restriction with Big-M?
        for t in self._T:
            for p in self._P:
                for j in self._N:
                    self.m.addConstr(self._Ujpt(j, p, t) <= self._Ojpt[j, p, t] * self._M)
        # 8.5 Request restriction with Big-M?
        for t in self._T:
            for p in self._P:
                for j in self._N:
                    pass
                    self.m.addConstr(self._Wjpt(j, p, t) <= self._Qjpt[j, p, t] * self._M)
    # Optimizes set objective and eliminates Outputs
    def set_optimize(self):
        obj = sum(self._Dij[i][j] * self._Xijpt[i, j, p, t] for i in self._N for j in self._N for p in self._P for t in self._T if i != j)
        self.m.setObjective(obj, GRB.MINIMIZE)
        self.m.Params.OutputFlag = 0
    # Gets all variables named Xijpt for subtourelim and subtour methods
    def get_x(self):
        global var_x
        var_x = []
        var_x = self._Xijpt
    # subtourelim staticmethod asigns Lazy restrictions if Callback and len(Subtour) satisfaction conditions are met
    # Adapted from original at https://www.gurobi.com/documentation/9.0/examples/tsp_py.html
    @staticmethod
    def subtourelim(model, where):
        global var_x, lazy_glob, callbacks_glob, houses_per_period
        n = houses_per_period
        if where == GRB.Callback.MIPSOL:
            vals = model.cbGetSolution(var_x)
            selected = tuplelist()
            for i in range(houses_per_period):
                for j in range(houses_per_period):
                    if vals[i, j, 0, 0] > 0.5 :
                        selected.append((i,j))
            tour = subtour(selected)
            if len(tour) < n:
                combinationF = list(combinations(tour, 2))
                if len(combinationF) == 1:
                    expr = len(tour) - 1
                    model.cbLazy(var_x[combinationF[0][1], combinationF[0][0], 0, 0] + var_x[combinationF[0][0], combinationF[0][1], 0, 0] <= expr)
                    lazy_glob += 1
                else:
                    expr = len(tour) - 1
                    sumarapida = 0 
                    for i in tour:
                        for j in tour:
                            sumarapida += var_x[i, j, 0, 0] + var_x[j, i, 0, 0]
                    model.cbLazy(sumarapida <= expr)
                    lazy_glob += 1
            callbacks_glob += 1
    # fix_sub function optimizes for subtourelim and "actual" tuplelist of edges
    # Adapted from original at https://www.gurobi.com/documentation/9.0/examples/tsp_py.html
    def fix_sub(self):
        global var_x
        n = self.HOUSES_PER_PERIOD
        self.m.Params.lazyConstraints = 1
        self.m.optimize(self.subtourelim)
        selected = tuplelist()
        for i in range(self.HOUSES_PER_PERIOD):
            for j in range(self.HOUSES_PER_PERIOD):
                if var_x[i, j, 0, 0].X > 0.5:
                    selected.append((i,j))

        tour = subtour(selected)
        assert len(tour) == n
        self.tourfinal = tour
        self.m.write('sols/SolutionForID_'+ str(self.result_id) + '.sol')
    # Drops final solution for front-end parse
    def drop_sol(self):
        solutions = []
        for i in self._N:
            for j in self._N:
                if self._Xijpt[i,j,0,0].X != 0:
                    solutions.append([i,j])
        return solutions
    # Drops final objective for front-end parse
    def drop_obj(self):
        return round(self.m.objVal, 3)
    # Drops final tour for front-end parse
    def drop_callback(self):
        return self.tourfinal
    # Drops ammount of callbakcs for front-end parse
    def drop_callbacks(self):
        global callbacks_glob
        return callbacks_glob
    # Drops ammount of lazy constraints for front-end parse
    def drop_lazy(self):
        global lazy_glob
        return lazy_glob