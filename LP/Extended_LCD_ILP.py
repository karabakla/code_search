from calendar import c
from concurrent.futures import ProcessPoolExecutor, as_completed, thread
import csv
import math
import os
import time
import traceback
from typing import Optional, Tuple
from gurobipy import GRB, quicksum, Model, Env
from KnownPaperResults.KnownResults import get_upper_bound_dimension
from LP.Extended_ILP import Solve_Extended_ILP
from Utils.File_Cache import File_Cache
from LP_Utils import gilbert_varshamov_bound_find_lower_dual_distance, gilbert_varshamov_linear_bound_k, krawtchouk
from sage.all import codes, binomial, cached_method, RR # type: ignore

from sage.coding.code_bounds import dimension_upper_bound # type: ignore

def gurobi_status_to_str(status):
    """
    LOADED          = 1
    OPTIMAL         = 2
    INFEASIBLE      = 3
    INF_OR_UNBD     = 4
    UNBOUNDED       = 5
    CUTOFF          = 6
    ITERATION_LIMIT = 7
    NODE_LIMIT      = 8
    TIME_LIMIT      = 9
    SOLUTION_LIMIT  = 10
    INTERRUPTED     = 11
    NUMERIC         = 12
    SUBOPTIMAL      = 13
    INPROGRESS      = 14
    USER_OBJ_LIMIT  = 15
    WORK_LIMIT      = 16
    MEM_LIMIT       = 17
    """
    dict_status = { 1: "LOADED", 2: "OPTIMAL", 3: "INFEASIBLE", 4: "INF_OR_UNBD", 5: "UNBOUNDED", 6: "CUTOFF", 7: "ITERATION_LIMIT", 8: "NODE_LIMIT", 9: "TIME_LIMIT", 10: "SOLUTION_LIMIT", 11: "INTERRUPTED", 12: "NUMERIC", 13: "SUBOPTIMAL", 14: "INPROGRESS", 15: "USER_OBJ_LIMIT", 16: "WORK_LIMIT", 17: "MEM_LIMIT"}
    return dict_status.get(status, "UNKNOWN")

def Solve_Extended_LCD_ILP(q, n, d, k_lo, k_up, krawtchouk_cache:dict,  threads_count) -> Optional[str|float]:
    print(f"\nSolving {q}, {n}, {d}, {k_lo}, {k_up}")
    with Model("mip") as model:
        model.params.OutputFlag =1 # silent mode
        model.params.LogToConsole = 0
        model.params.LogFile = f"outputs/logs/gurobi{q}_{n}_{d}_{k_lo}.log"
        if os.path.exists(model.params.LogFile):
            os.remove(model.params.LogFile)
        # Known settings
        # A_0 = 1
        # A_1 ... A_{d-1} = 0
        # A_d .. A_n >= 0
        # sum( A_i*Krawtchouk(n, q, i, j) ) >= 0 for j in 0 .. n+1
        # for simplicity, we will use variables A_d .. A_n in the model so there is n-d +1 variables

        A = model.addVars(n-d+1, vtype=GRB.INTEGER, lb=0, name="A")

        model_prep_start = time.time()

        dual_d0 = 0 #gilbert_varshamov_bound_find_lower_dual_distance(q, n, k_lo)

        def get_Krawtchouk_0(j):
            return (q-1)**j * binomial(n, j)

        A[0].lb = 1
        A[0].ub = (q-1)**d * binomial(n, d)
        for j in range(d+1, n+1):
            A[j-d].lb = 0
            A[j-d].ub = (q-1)**j * binomial(n, j)


        for j in range(1, n+1):
            lhs = quicksum(A[i-d] * krawtchouk_cache.get((n, q, j, i))/get_Krawtchouk_0(j) for i in range(d, n+1))
            rhs = -1

            if j < dual_d0:
                model.addLConstr(lhs == rhs)
            else:
                model.addLConstr(lhs >= rhs)

        for j in range(max(d, dual_d0), n+1):
            lhs = A[j-d] *(q**k_lo/ get_Krawtchouk_0(j))
            rhs = quicksum(A[i-d] * (1 - krawtchouk_cache.get((n, q, j, i))/get_Krawtchouk_0(j) ) for i in range(d, n+1))

            model.addLConstr(lhs <= rhs)

            # A_j = A[j-d]
            # B_j = 1/q**k_up*quicksum(A[i-d] * krawtchouk_cache.get((n, q, j, i))  for i in range(d, n+1))

            # lhs = (A_j + B_j) / ((q-1)**j * binomial(n, j))
            # rhs = 1
            # model.addLConstr(lhs <= rhs)

        #model.addConstr(quicksum(A[i-d] for i in range(d, n+1)) >= q**k_lo)
        # model.addConstr(quicksum(A[i-d] for i in range(d, n+1)) <= q**(k_up +0.99999))

        model.setObjective(quicksum(A[i-d] for i in range(d, n+1)), GRB.MAXIMIZE)

        model_prep_duration = time.time() - model_prep_start

        # set max threads
        model.params.Threads = max(threads_count,1)
        model.params.Method = GRB.METHOD_DETERMINISTIC_CONCURRENT
        model.params.ConcurrentMIP = max(threads_count,1)
        model.params.Quad = 1
        model.params.NumericFocus = 3

        model.params.IntFeasTol = 1e-6
        model.params.FeasibilityTol = 1e-9
        model.params.OptimalityTol = 1e-3
        model.params.MIPGap = 1e-1
        model.params.MIPGapAbs = 1e-1

        model.params.MIPFocus = 3
        model.params.ObjScale = -0.75
        # model.params.ScaleFlag = 3
        model.params.Cutoff = q**k_lo

        #model.params.Cuts = GRB.CUTS_CONSERVATIVE
        model.params.MIPSepCuts = GRB.CUTS_CONSERVATIVE
        model.params.PreCrush = 1
        model.params.Presolve = GRB.PRESOLVE_CONSERVATIVE # type: ignore
        model.params.Aggregate = 1

        # memory soft limit to 48 GB available 64 GB
        model.params.SoftMemLimit = 32
        model.params.MemLimit = 48
        model.params.NodefileStart = 100
        model.params.NodefileDir = "outputs/nodefiles"

        # model.params.BestObjStop = q**k_up

        model.params.TimeLimit = 4*60*60 # 4 hour

        # model.write(f"outputs/models/Extended_LCD_ILP_{q}_{n}_{d}_{k_lo}.lp")
        # model.write(f"outputs/models/Extended_LCD_ILP_{q}_{n}_{d}_{k_lo}.mps")


        def is_model_feasible(model:Model) -> Tuple[bool, bool, float]:
            if model.Status != GRB.Status.OPTIMAL:
                print(f"Model status is not optimal: {gurobi_status_to_str(model.Status)}")
                return False, False, 0

            bound = math.log(model.ObjVal +1, q)
            bound_int = int(bound)
            if bound_int < k_lo:
                print(f"Bound {bound_int} is less than k0 {k_lo}\n")
                return False, False, 0

            if bound_int > k_up:
                print(f"Bound {bound_int} is greater than k_up {k_up}\n")
                return False, True, 0

            if bound_int > n:
                print(f"Bound {bound_int} is greater than n {n}\n")
                return False, False, 0

            return True, False, bound

       
        def solve_model(model:Model):
            model.presolve()
            model.update()
            model.optimize()
            return model

        best_bound = None
        for trial in range(11):
            model_start_time = time.time()
            solve_model(model)
            model_duration = time.time() - model_start_time
            
            model_feasible, bounded_upper_bound, bound = is_model_feasible(model)

            if model_feasible:
                print(f"Model prep duration: {model_prep_duration} Model optimization duration: {model_duration}\n")
                return bound
            
            # Keep the best bound and try other settings if the model is not feasible
            if bounded_upper_bound:
                best_bound = f"{k_up}up"

            if trial == 0:
                model.params.MIPFocus = 2
                continue

            if trial == 1:
                model.params.MIPFocus = 1
                model.params.ObjScale = -0.5
                continue

            if trial == 2: 
                model.params.IntFeasTol = 1e-4
                model.params.ObjScale = -0.4
                model.params.MIPFocus = 2
                model.params.NumericFocus = 2
                continue
            if trial == 3:
                model.params.IntFeasTol = 1e-2
                model.params.FeasibilityTol = 1e-2
                model.params.OptimalityTol = 1e-2
                model.params.ObjScale = -0.25
                model.params.NumericFocus = 1
                continue
            if trial == 4:
                model.params.IntFeasTol = 1e-1
                model.params.ObjScale = -0.1
                model.params.MIPFocus = 1
                continue

            if trial == 6:
                model.params.IntFeasTol = 1e-1
                model.params.ObjScale = 0
                model.params.MIPFocus = 1
                continue

            if trial == 7:
                model.params.IntFeasTol = 1e-1
                model.params.ObjScale = -0.1
                model.params.MIPFocus = 2
                continue

            if trial == 8:
                model.params.IntFeasTol = 1e-1
                model.params.ObjScale = -0.1
                model.params.MIPFocus = 3
                continue

            if trial == 9:
                model.params.IntFeasTol = 1e-2
                model.params.ObjScale = -0.1
                continue

            if trial == 10:
                model.params.IntFeasTol = 1e-3
                model.params.ObjScale = -0.25
                continue
        
        return best_bound

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
    k_up = dimension_upper_bound(n, d, q) # type: ignore

    if k_lo == k_up:
        return k_lo

    return None

def compute_lcd_bound(q, n, d, krawtchouk_cache:dict, threads_count) -> Tuple[int, int, int, Optional[float|str]]:
    k_alg = compute_algebraic_bound(q, n, d)

    if k_alg is not None:
        return q, n, d, k_alg

    k_lo = gilbert_varshamov_linear_bound_k(q, n, d)
    k_up = dimension_upper_bound(n, d, q) # type: ignore

    try:
        bound = Solve_Extended_LCD_ILP(q, n, d, k_lo, k_up, krawtchouk_cache, threads_count)
    except:
        print(f"Error in ({q}, {n}, {d}): {traceback.format_exc()}")
        return q, n, d, None

    return q, n, d, bound


# def is_integer(x, tol):
#     return abs(x - round(x)) < tol

# def to_int(x, tol=1e-9):
#     if is_integer(x, tol):
#         return int(round(x))
#     return int(x)

def check_k0_conjecture(q, n, d, bound:int) -> bool:
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

start_time = time.time()
q, n, d = 3, 53, 4
k_lo = gilbert_varshamov_linear_bound_k(q, n, d)
k_up = int(dimension_upper_bound(n, d, q)) # type: ignore
solve_result = Solve_Extended_LCD_ILP(q, n, d, k_lo, k_up, get_krawtchouk_cached(n, q, d), 24)
duration = time.time() - start_time
print(f"({q}, {n}, {d}, {k_lo}, {k_up}): {solve_result} in {duration} seconds")


if __name__ == "__main__":
    q = 3
    n_max = 60
    threads_count = 24
    sch_count = 1 # max 24

    output_array = [['0' for x in range(n_max)] for y in range(n_max)]
    output_array_raw= [['0' for x in range(n_max)] for y in range(n_max)]

    # read output file if it exists and continue from there
    if not os.path.exists(f"outputs/models"):
        os.makedirs("outputs/models")
    if not os.path.exists(f"outputs/nodefiles"):
        os.makedirs("outputs/nodefiles")

    if os.path.exists(f"outputs/LCD_ILP_output_{q}.csv"):
        with open(f"outputs/LCD_ILP_output_{q}.csv", 'r') as file:
            reader = csv.reader(file)
            output_array = list(reader) # type: ignore
            output_array = [[x for x in row] for row in output_array]

    if os.path.exists(f"outputs/LCD_ILP_output_{q}_raw.csv"):
        with open(f"outputs/LCD_ILP_output_{q}_raw.csv", 'r') as file:
            reader = csv.reader(file)
            output_array_raw = list(reader) # type: ignore
            output_array_raw = [[x for x in row] for row in output_array_raw] # type: ignore


    krawtchouk_file_cache = File_Cache(f"outputs/cache/krawtchouk_file_cache_{q}.json")

    n_and_d_array = [
            [n,d] for n in range(1, n_max+1) for d in range(1, n)
            if (int(output_array[n-1][d-1].rstrip('*').rstrip('up')) == 0 or int(output_array[n-1][d-1].rstrip('*').rstrip('up')) == -1 or not check_k0_conjecture(q, n, d, int(output_array[n-1][d-1].rstrip('*').rstrip('up'))))
        ]

    # open for the first time
    # for n, d in n_and_d_array:
    #     k_up = get_upper_bound_dimension(q, n, d)
    #     if isinstance(k_up, int):
    #         output_array[n-1][d-1] = f"{k_up}*"
    #         continue
    #     try:
    #         k_alg = compute_algebraic_bound(q, n, d)

    #         if k_alg is not None:
    #             output_array[n-1][d-1] = f"{k_alg}*"
    #             continue
    #     except:
    #         pass

    # with open(f"outputs/LCD_ILP_output_{q}.csv", 'w', newline='') as file:
    #     writer = csv.writer(file)
    #     writer.writerows(output_array)

    # n_and_d_array = sorted(n_and_d_array, key=lambda x: x[0]-x[1])
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
        futures = [executor.submit(compute_lcd_bound, q, n, d, get_krawtchouk_cached(n, q, d, krawtchouk_file_cache), threads_count/sch_count) for n, d in n_and_d_array]

        for future in as_completed(futures):
            try:
                completed_tasks += 1
                q, n, d, bound = future.result()
                k_lo = gilbert_varshamov_linear_bound_k(q, n, d)
                k_up = dimension_upper_bound(n, d, q) # type: ignore
                print(f"Completed ({q}, {n}, {d}, {k_lo}, {k_up}): {bound} {completed_tasks}/{total_tasks}")

                bound_int = int(bound) if isinstance(bound, float) else -1

                if bound is None:
                    bound = -1

                output_array[n-1][d-1] = f"{bound_int}" if bound_int> 0 else bound # type: ignore
                output_array_raw[n-1][d-1] = bound if bound is not None else -1 # type: ignore

                with open(f"outputs/LCD_ILP_output_{q}.csv", 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerows(output_array)

                with open(f"outputs/LCD_ILP_output_{q}_raw.csv", 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerows(output_array_raw)
            except:
                print(f"Error in task {traceback.format_exc()}")
                continue