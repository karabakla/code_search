from calendar import c
from concurrent.futures import ProcessPoolExecutor, as_completed
import csv
import math
import os
import time
from typing import Optional, Tuple
from gurobipy import GRB, quicksum, Model
from LP.Extended_ILP import Solve_Extended_ILP
from Utils.File_Cache import File_Cache
from LP_Utils import gilbert_varshamov_bound_find_lower_dual_distance, gilbert_varshamov_linear_bound_k, krawtchouk
from sage.all import codes, binomial, cached_method, RR # type: ignore

from sage.coding.code_bounds import codesize_upper_bound # type: ignore


def Solve_Extended_LCD_ILP(q, n, d, k_lo, k_up, krawtchouk_cache:dict,  threads_count):
    model = Model("mip1")
    
    model.params.OutputFlag = 0 # silent mode
        
    # Known settings
    # A_0 = 1
    # A_1 ... A_{d-1} = 0
    # A_d .. A_n >= 0
    # sum( A_i*Krawtchouk(n, q, i, j) ) >= 0 for j in 0 .. n+1
    # for simplicity, we will use variables A_d .. A_n in the model so there is n-d +1 variables

    A = model.addVars(n+1, vtype=GRB.INTEGER, lb=0, name="A")
    
    model_prep_start = time.time()
    
    dual_d0 = gilbert_varshamov_bound_find_lower_dual_distance(q, n, k_lo)
     
    A[0].lb = 1
    A[0].ub = 1
    for j in range(1, d):
        A[j].lb = 0
        A[j].ub = 0
    
    A[d].lb = 1
    
    for j in range(d, n+1):
        A[j].lb = 0
        A[j].ub = (q-1)**j * binomial(n, j) + 1
    
  
    for j in range(1, n+1):
        lhs = quicksum(A[i] * krawtchouk_cache.get((n, q, j, i)) for i in range(d, n+1))
        rhs = -(q-1)**j * binomial(n, j)
        
        if j < dual_d0:
            model.addLConstr(lhs == rhs)
        else:
            model.addLConstr(lhs >= rhs)
    
    for j in range(d, n+1):
        A_j = A[j]
        B_j = 1

        # if j < d:
        #     A_j = 0
        
        if j != 1:
            if j < dual_d0:
                B_j = 0
            else:
                B_j = 1/q**k_lo * quicksum(A[i] * krawtchouk_cache.get((n, q, j, i)) for i in range(0, n+1))
        
        lhs = A_j + B_j
        rhs = (q-1)**j * binomial(n, j)
        model.addLConstr(lhs <= rhs)
            
    # model.addConstr(A[0] >= 1) 
    
    # model.addConstr(quicksum(A[i-d] for i in range(d, n+1)) >= (q**k_lo -0.99))
    # model.addConstr(quicksum(A[i-d] for i in range(d, n+1)) <= q**(k_up +0.99))    
    
    model.setObjective(quicksum(A[i-d] for i in range(d, n+1)), GRB.MAXIMIZE)
   
    model_prep_duration = time.time() - model_prep_start
         
    # set max threads
    model.params.Threads = max(threads_count,1)
    model.params.Method = GRB.METHOD_DETERMINISTIC_CONCURRENT
    model.params.ConcurrentMIP = 1
    model.params.Quad = 1
    model.params.NumericFocus = 3
    
    # model.params.IntFeasTol = 1e-3
    # model.params.FeasibilityTol = 1e-3
    # model.params.OptimalityTol = 1e-3
    # model.params.MIPGap = 1e-3
    
    model.params.MIPFocus = 2
    model.params.ObjScale =  -0.5
    # model.params.Cutoff = q**k_lo
    
    # model.params.Cuts = GRB.CUTS_CONSERVATIVE
    # model.params.PreCrush = 1
    # model.params.Presolve = GRB.PRESOLVE_CONSERVATIVE # type: ignore
    # model.params.Aggregate = 1
    
    # # memory soft limit to 57 GB
    # model.params.SoftMemLimit = 57 * 1024 * 1024 * 1024
    # model.params.NodeLimit = 10000000
    # model.params.NodefileStart = 100
    # model.params.NodefileDir = "outputs/nodefiles"

    # model.params.BestObjStop = q**k_up

    # model.write(f"outputs/models/Extended_LCD_ILP_{q}_{n}_{d}_{k_lo}.lp")
    # model.write(f"outputs/models/Extended_LCD_ILP_{q}_{n}_{d}_{k_lo}.mps")
    
    #model.presolve()
    model.update()
    
    # model.write(f"outputs/models/Extended_LCD_ILP_{q}_{n}_{d}_{k_lo}.lp")
    # model.write(f"outputs/models/Extended_LCD_ILP_{q}_{n}_{d}_{k_lo}.mps")
    
    model_start_time = time.time()
    
    model.optimize()

    model_duration = time.time() - model_start_time
    
    print(f"Model prep duration: {model_prep_duration} Model optimization duration: {model_duration}")
    
    if model.status == GRB.Status.OPTIMAL:
        if model.ObjVal <= 0:
            return None
        bound = math.log(model.ObjVal +1, q)
        bound_int = to_int(bound)
        if bound_int < k_lo:
            print(f"Bound {bound} is less than k0 {k_lo}")
            return None
        
        if bound_int > k_up:
            print(f"Bound {bound} is greater than k_up {k_up}")
            return None
        
        if bound_int > n:
            print(f"Bound {bound} is greater than n {n}")
            return None
    
        
        print([1] + [0]*d + [A[i].X for i in range(n-d+1)])
        return bound
    
    return None

def compute_lcd_bound(q, n, d, krawtchouk_cache:dict, threads_count) -> Tuple[int, int, int, Optional[float]]:
    if d == 1: # trivial code
        return q, n, d, n
    if q == 2:
        if n % 2 == 0:
            if n == d:
                return q, n, d, 0
            if d == 2:
                return q, n, d, n-2
        else:
            if n == d:
                return q, n, d, 1
            if d == 2:
                return q, n, d, n-1
    
    k_lo = gilbert_varshamov_linear_bound_k(q, n, d)
    k_up = math.log(codesize_upper_bound(n, d, q), q)
    bound = Solve_Extended_LCD_ILP(q, n, d, k_lo, k_up, krawtchouk_cache, threads_count)
    if bound is None or k_lo > bound:
        return q, n, d, -1
    
    return q, n, d, bound
   

def is_integer(x, tol):
    return abs(x - round(x)) < tol

def to_int(x, tol=1e-6):
    if is_integer(x, tol):
        return int(round(x))
    return int(x)

def check_k0_conjecture(q, n, d, bound):
    k0 = gilbert_varshamov_linear_bound_k(q, n, d)
    
    return k0 <= bound

@cached_method
def get_krawtchouk_cached(n, q, d, file_cache:Optional[File_Cache] = None) -> dict:
    krawtchouk_cache = {}
    for j in range(0, n+1):
        for i in range(0, n+1):
            if file_cache is not None:
                cache_key = f"{n}_{q}_{j}_{i}"
                if file_cache.contains(cache_key):
                    krawtchouk_cache[(n, q, j, i)] = file_cache.get(cache_key)
                    continue
            krawtchouk_cache[(n, q, j, i)] = krawtchouk(n, q, j, i)
    return krawtchouk_cache

# test method

start_time = time.time()
q, n, d = 2, 19,7
k_lo = gilbert_varshamov_linear_bound_k(q, n, d)
k_up = int(math.log(codesize_upper_bound(n, d, q), q))
solve_result = Solve_Extended_LCD_ILP(q, n, d, k_lo, k_up, get_krawtchouk_cached(n, q, d), 12)
duration = time.time() - start_time
print(f"({q}, {n}, {d}): {solve_result} in {duration} seconds")