import math
from gurobipy import GRB, quicksum, Model
from LP_Utils import krawtchouk
from sage.all import codes,binomial, RR # type: ignore

def Solve_Extended_ILP(q, n, d):
    model = Model("Extended ILP")
    
    model.params.OutputFlag = 0 # silent mode
        
    # Known settings
    # A_0 = 1
    # A_1 ... A_{d-1} = 0
    # A_d .. A_n >= 0
    # sum( A_i*Krawtchouk(n, q, i, j) ) >= 0 for j in 0 .. n+1
    # for simplicity, we will use variables A_d .. A_n in the model so there is n-d +1 variables

    A = model.addVars(n-d+1, vtype=GRB.INTEGER, lb=0, name="A")
    
    def get_A(i):
        return A[i-d] if i >=d else 0
            
    for j in range(1, n+1):
        model.addConstr(quicksum(get_A(i) * krawtchouk(n, q, j, i) for i in range(1, n+1)) >= -(q-1)**j * binomial(n, j))
    
    model.setObjective(quicksum(get_A(i) for i in range(n+1)), GRB.MAXIMIZE)
  
    model.optimize()

    
    if model.status == GRB.Status.OPTIMAL:
        if model.ObjVal <= 0:
            return None
        #return math.log(model.ObjVal, q)
        # sol = [1] + [A[i].X for i in range(n-d+1)]
        bound = math.log(model.ObjVal +1, q)
        return bound
    
    return None

# q = 2
# n = 32
# d = 7

# # A, p, val = codes.bounds.delsarte_bound_hamming_space(n, d, q, return_data=True)
# # p.show()
# # print(RR(val))
# print(Solve_Extended_ILP(q, n, d))