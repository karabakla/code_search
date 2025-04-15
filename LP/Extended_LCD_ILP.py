from calendar import c
from concurrent.futures import ProcessPoolExecutor, as_completed
import csv
import math
import os
import time
from typing import Optional, Tuple
from gurobipy import GRB, quicksum, Model, Env
from KnownPaperResults.KnownResults import get_exact_upper_bound_dimension
from LP.Extended_ILP import Solve_Extended_ILP
from Utils.File_Cache import File_Cache
from LP_Utils import gilbert_varshamov_bound_find_lower_dual_distance, gilbert_varshamov_linear_bound_k, krawtchouk
from sage.all import codes, binomial, cached_method, RR # type: ignore

from sage.coding.code_bounds import codesize_upper_bound # type: ignore


def Solve_Extended_LCD_ILP(q, n, d, k_lo, k_up, krawtchouk_cache:dict,  threads_count):
    with Model("mip") as model:
        model.params.OutputFlag = 0 # silent mode
        model.params.LogToConsole = 0
        model.params.LogFile = "outputs/logs/gurobi.log"
        # Known settings
        # A_0 = 1
        # A_1 ... A_{d-1} = 0
        # A_d .. A_n >= 0
        # sum( A_i*Krawtchouk(n, q, i, j) ) >= 0 for j in 0 .. n+1
        # for simplicity, we will use variables A_d .. A_n in the model so there is n-d +1 variables

        A = model.addVars(n-d+1, vtype=GRB.INTEGER, lb=0, name="A")
        
        model_prep_start = time.time()
        
        dual_d0 =0 #gilbert_varshamov_bound_find_lower_dual_distance(q, n, k_lo)
        
        A[0].lb = 1
        A[0].ub = (q-1)**d * binomial(n, d)
        for j in range(d+1, n+1):
            A[j-d].lb = 0
            A[j-d].ub = (q-1)**j * binomial(n, j)
            

        for j in range(1, n+1):
            lhs = quicksum(A[i-d] * krawtchouk_cache.get((n, q, j, i)) for i in range(d, n+1))
            rhs = -(q-1)**j * binomial(n, j)
            
            if j < dual_d0 and dual_d0 > d:
                model.addLConstr(lhs == rhs)
            else:
                model.addLConstr(lhs >= rhs)
        
        for j in range(d, n+1):
            A_j = A[j-d]
            B_j = 0
            if j >= dual_d0:
                B_j = 1/q**k_lo * quicksum(A[i-d] * krawtchouk_cache.get((n, q, j, i)) for i in range(d, n+1))
                
            lhs = A_j + B_j
            rhs = (q-1)**j * binomial(n, j)
                        
            model.addLConstr(lhs <= rhs)
            
        # model.addConstr(quicksum(A[i-d] for i in range(d, n+1)) >= q**k_lo)
        # model.addConstr(quicksum(A[i-d] for i in range(d, n+1)) <= q**(k_up +0.99999))    
        
        model.setObjective(quicksum(A[i-d] for i in range(d, n+1)), GRB.MAXIMIZE)
    
        model_prep_duration = time.time() - model_prep_start
            
        # set max threads
        model.params.Threads = max(threads_count,1)
        model.params.Method = GRB.METHOD_DETERMINISTIC_CONCURRENT
        model.params.ConcurrentMIP = 1
        model.params.Quad = 1
        model.params.NumericFocus = 3
        
        model.params.IntFeasTol = 1e-6
        model.params.FeasibilityTol = 1e-3
        model.params.OptimalityTol = 1e-3
        model.params.MIPGap = 1e-1
        
        model.params.MIPFocus = 1
        model.params.ObjScale =  -1
        model.params.Cutoff = q**k_lo
        
        model.params.Cuts = GRB.CUTS_CONSERVATIVE
        model.params.PreCrush = 1
        model.params.Presolve = GRB.PRESOLVE_CONSERVATIVE # type: ignore
        model.params.Aggregate = 1
        
        # memory soft limit to 57 GB
        model.params.SoftMemLimit = 57 * 1024 * 1024 * 1024
        model.params.NodeLimit = 10000000
        model.params.NodefileStart = 100
        model.params.NodefileDir = "outputs/nodefiles"

        model.params.BestObjStop = q**k_up

        # model.write(f"outputs/models/Extended_LCD_ILP_{q}_{n}_{d}_{k_lo}.lp")
        # model.write(f"outputs/models/Extended_LCD_ILP_{q}_{n}_{d}_{k_lo}.mps")
        
        model.presolve()
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
        
            
            # print([1] + [0]*d + [A[i].X for i in range(n-d+1)])
            return bound
    
    return None

def compute_algebraic_bound(q, n, d) -> int | None:
    if d == 1: # trivial code
        return n
    if q == 2:
        if n % 2 == 0:
            if n == d:
                return 0
            if d == 2:
                return n-2
        else:
            if n == d:
                return 1
            if d == 2:
                return n-1
    
    k_lo = gilbert_varshamov_linear_bound_k(q, n, d)
    k_up = int(math.log(codesize_upper_bound(n, d, q), q))
    
    if k_lo == k_up:
        return k_lo
    
    return None

def compute_lcd_bound(q, n, d, krawtchouk_cache:dict, threads_count) -> Tuple[int, int, int, Optional[float]]:
    k_alg = compute_algebraic_bound(q, n, d)
    
    if k_alg is not None:
        return q, n, d, k_alg
    
    k_lo = gilbert_varshamov_linear_bound_k(q, n, d)
    k_up = int(math.log(codesize_upper_bound(n, d, q), q))
    
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
    for j in range(1, n+1):
        for i in range(d, n+1):
            if file_cache is not None:
                cache_key = f"{n}_{q}_{j}_{i}"
                if file_cache.contains(cache_key):
                    krawtchouk_cache[(n, q, j, i)] = file_cache.get(cache_key)
                    continue
            krawtchouk_cache[(n, q, j, i)] = krawtchouk(n, q, j, i)
    return krawtchouk_cache

# test method

# start_time = time.time()
# q, n, d = 2, 49, 5
# k_lo = gilbert_varshamov_linear_bound_k(q, n, d)
# k_up = int(math.log(codesize_upper_bound(n, d, q), q))
# solve_result = Solve_Extended_LCD_ILP(q, n, d, k_lo, k_up, get_krawtchouk_cached(n, q, d), 12)
# duration = time.time() - start_time
# print(f"({q}, {n}, {d}): {solve_result} in {duration} seconds")


if __name__ == "__main__":
    q = 2
    n_max = 30
    sch_count = 2 # max 12
        
    output_array = [[0 for x in range(n_max)] for y in range(n_max)] 
    output_array_raw= [[0 for x in range(n_max)] for y in range(n_max)] 

    # read output file if it exists and continue from there
    if not os.path.exists(f"outputs/models"):
        os.makedirs("outputs/models")
    if not os.path.exists(f"outputs/nodefiles"):
        os.makedirs("outputs/nodefiles")
        
    if os.path.exists(f"outputs/LCD_ILP_output_{q}.csv"):
        with open(f"outputs/LCD_ILP_output_{q}.csv", 'r') as file:
            reader = csv.reader(file)
            output_array = list(reader) # type: ignore
            output_array = [[int(x) for x in row] for row in output_array]
            
        with open(f"outputs/LCD_ILP_output_{q}_raw.csv", 'r') as file:
            reader = csv.reader(file)
            output_array_raw = list(reader) # type: ignore
            output_array_raw = [[float(x) for x in row] for row in output_array_raw] # type: ignore
    
    krawtchouk_file_cache = File_Cache(f"outputs/cache/krawtchouk_file_cache_{q}.json")
    
    n_and_d_array = [
            [n,d] for n in range(1, n_max+1) for d in range(1, n) 
            if (output_array[n-1][d-1] == 0 or output_array[n-1][d-1] == -1 or not check_k0_conjecture(q, n, d, output_array[n-1][d-1]))
        ]
    
    # open for the first time
    # for n, d in n_and_d_array:
    #     k_up = get_upper_bound_dimension(q, n, d)
    #     if isinstance(k_up, int):
    #         output_array[n-1][d-1] = k_up
    #         continue
    #     try:
    #         k_alg = compute_algebraic_bound(q, n, d)
                
    #         if k_alg is not None:
    #             output_array[n-1][d-1] = k_alg
    #             continue
    #     except:
    #         pass
    
    # with open(f"outputs/LCD_ILP_output_{q}.csv", 'w', newline='') as file:
    #     writer = csv.writer(file)
    #     writer.writerows(output_array)
    
    # n_and_d_array = sorted(n_and_d_array, key=lambda x: x[0])
    # for n, d in n_and_d_array:
    #     for j in range(1, n+1):
    #         for i in range(d, n+1):
    #             cache_key = f"{n}_{q}_{j}_{i}"
    #             if not krawtchouk_file_cache.contains(cache_key):
    #                     krawtchouk_file_cache.set(cache_key, krawtchouk(n, q, j, i))
    
    # krawtchouk_file_cache.flush()
    
    total_tasks = len(n_and_d_array)
    print(f"Total tasks: {total_tasks}")
    
    completed_tasks = 0
    with ProcessPoolExecutor(max_workers=sch_count, max_tasks_per_child=1) as executor:
        futures = [executor.submit(compute_lcd_bound, q, n, d, get_krawtchouk_cached(n, q, d, krawtchouk_file_cache), 12/sch_count) for n, d in n_and_d_array]
        
        for future in as_completed(futures):
            completed_tasks += 1
            q, n, d, bound = future.result()
            print(f"Completed ({q}, {n}, {d}): {bound} {completed_tasks}/{total_tasks}")
                                    
            output_array[n-1][d-1] = to_int(bound) if bound is not None else -1 # type: ignore
            output_array_raw[n-1][d-1] = bound if bound is not None else -1 # type: ignore
            
            with open(f"outputs/LCD_ILP_output_{q}.csv", 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(output_array)
                
            with open(f"outputs/LCD_ILP_output_{q}_raw.csv", 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(output_array_raw)