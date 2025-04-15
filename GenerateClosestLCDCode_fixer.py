from collections import deque
from concurrent.futures import ProcessPoolExecutor, as_completed
import csv
import math
import multiprocessing as mp
import os
import random
import subprocess
import sys
import traceback
from typing import Any, Callable, Deque, Dict, List, Optional, Set, Tuple, overload

from KnownPaperResults import KnownResults
from LCDCodePool.GetClosestLCD import get_lcd_codes_q, get_lcd_codes_q_excluding_quasi_cyclic
from Utils.File_Cache import File_Cache
from Utils.Code_Utils import safe_minimum_distance
from Utils.MagmaUtils import MagmaSession
from Utils.Types import BdlcLcdCodeRecord, CyclicCodeRecord, GeneratorMatrixRecord, LinearCodeRecord, QuasiCyclicCodeRecord
from Utils.CodeConstruction.CodeConstUtils import is_lcd_code, lemma_4_1_generate_new_code_from, prop_4_2_generate_new_code_from, theorem_4_3_extended_const_method_generate_new_code_from, theorem_4_7_generate_new_code_from
from sage.coding.linear_code import LinearCode # type: ignore
from sage.all import matrix, GF, cached_method # type: ignore
import pickle
from sage.coding.code_bounds import codesize_upper_bound # type: ignore
import signal, psutil # type: ignore

# We have multiple lcd code extension methods:
# lemma_4_1_generate_new_code_from: given [n, k, d] -> [n-1, k-|indicies|, d'] or [n-|indicies|, k-T, d'] where T>= |indicies|
# prop_4_2_generate_new_code_from: given [n, k, d] -> [n+r, k, d] where r arbitrary
# theorem_4_3_extended_const_method_generate_new_code_from: given [n, k, d] -> [n+r, k+1, d] where r>=p for p=2, 3
# theorem_4_7_generate_new_code_from: given [n, k, d] -> [n+m, k+r, d'] where m and r arbitrary d'<= d

def create_magma_session(thread_count = 1):
    magma_session = MagmaSession(f"{os.getcwd()}/Utils/Magma/MagmaCodes", thread_count)
    magma_session.magma.set_seed(0)
    return magma_session


# def compare_codes(code1:LinearCodeRecord, code2:LinearCodeRecord) -> int:
#     if code1.k == 0 or code2.k == 0:
#         return 9999999999999999999
    
#     def calc_cost (code:LinearCodeRecord) -> int:
#         return code.n - code.k - code.d - 1
    
#     print(f"Comparing {code1}:{calc_cost(code1)} and {code2}:{calc_cost(code2)}")
#     return calc_cost(code1) - calc_cost(code2)
    

# def _to_linear_code_record(code:LinearCode):
#     q = code.base_ring().order()
#     n = code.length()
#     k = code.dimension()
#     min_distance = int(magma_session.magma.MinimumWeight(code))
#     new_code_record = LinearCodeRecord(q, n, k, min_distance, True)    
#     return new_code_record


def get_min_distance(code:LinearCode) -> int:
    # print(f"Min distance:{cyclic_code}, generator:{cyclic_code.generator_polynomial()}")
    # def get_min_distance_online_magma(C) -> int | None:        
    #     sleep(randint(1, 10)) # wait for a random time to avoid spamming the server
    #     return CyclicCodeMinDistance.get_min_distance(len(C.base_field()), C.length(), C.generator_polynomial())

    # magma_min_distance = get_min_distance_online_magma(cyclic_code)
    # if isinstance(magma_min_distance, int) and magma_min_distance > 0:
    #     return magma_min_distance
    
    # magma.SetNthreads(64)
    # magma_min_distance = magma.MinimumDistance(cyclic_code)
    # if isinstance(magma_min_distance, int) and magma_min_distance > 0:
    #     return magma_min_distance
    
    return safe_minimum_distance(code)

# common params for all code search records
class LinearCodeSearchRecordParams:
    def __init__(self, code:LinearCode, min_distance:Optional[int],  gen_objects:Any, construction_method:str):
        self.q:int = int(code.base_ring().order())
        self.n:int = int(code.length())
        self.k:int = int(code.dimension())
        self.d: int = int(min_distance) if min_distance is not None else int(get_min_distance(code))
           
        self.code_str = str(code)
        self.code_type = type(code)
        self.gen_objects:Any = gen_objects
        
        self.construction_method:str = str(construction_method)
    
    def __str__(self):
        return f"{self.q}_{self.n}_{self.k}_{self.d} {self.code_str}"
    
    def __repr__(self):
        return self.__str__()
    
    def __hash__(self) -> int:
        return hash(str(self))
    
    def __eq__(self, value: object) -> bool:
        return isinstance(value, LinearCodeSearchRecordParams) and self.q == value.q and self.n == value.n and self.k == value.k and self.d == value.d
    
class LinearCodeSearchRecordSerialized:
    def __init__(self, parent_code_serialized: Optional['LinearCodeSearchRecord'], code_record:'LinearCodeSearchRecord'):
        self.parent_code_serialized:Optional[LinearCodeSearchRecordSerialized] = parent_code_serialized.serialize() if parent_code_serialized is not None else None
        self.serialized_generator_matrix:bytes = pickle.dumps(code_record.code.generator_matrix())
        self.code_params:LinearCodeSearchRecordParams = code_record.code_params
        
    def to_linear_code_search_record(self) -> 'LinearCodeSearchRecord':
        linear_code = LinearCode(matrix(GF(self.code_params.q), pickle.loads(self.serialized_generator_matrix)))
        parent_code = None if self.parent_code_serialized is None else self.parent_code_serialized.to_linear_code_search_record()
      
        return LinearCodeSearchRecord(parent_code, linear_code, self.code_params)
    
class LinearCodeSearchRecord:
    def __init__(self, parent_code: Optional['LinearCodeSearchRecord'], code:LinearCode, code_params:LinearCodeSearchRecordParams):
        self.code_str = str(code)
        self.code = code
        self.parent_code = parent_code
        self.code_params = code_params
        self.parent_count:int = 0 if parent_code is None else parent_code.parent_count + 1
        
    def __str__(self):
        return str(self.code_params)
    
    def __repr__(self):
        return self.__str__()

    def __hash__(self) -> int:
        return hash(str(self))
    
    def __eq__(self, value) -> bool:
        return isinstance(value, LinearCodeSearchRecord) and self.code_params == value.code_params
    
    def __ne__(self, value) -> bool:
        return not self.__eq__(value)
        
    def is_n_k_equal(self, n:int, k:int) -> bool:
        return self.code.length() == n and self.code.dimension() == k    
    
    def serialize(self) -> LinearCodeSearchRecordSerialized:
        return LinearCodeSearchRecordSerialized(self.parent_code, self)

    def to_json(self) -> Dict[str, Any]:
        G = GeneratorMatrixRecord(self.code.generator_matrix()) # type: ignore
        return {
            "code": self.code_params.code_str,
            "GenMatrix": G.to_json(),
            "min_distance": self.code_params.d,
            "const_method_params": self.code_params.construction_method,
            "gen_objects": str(self.code_params.gen_objects),
            "parent_count": self.parent_count,
            "parent_code": self.parent_code.to_json() if self.parent_code is not None else None
        }
        
    def get_code_by_index(self, index:int) -> Optional['LinearCodeSearchRecord']:
        """
            0 is initial code
            1 is first parent code
            2 is second parent code
            ...
            last is itself
        """
        
        if index == 0:
            if self.parent_code is None:
                return self
            return self.parent_code.get_code_by_index(0)
        
        if index == self.parent_count:
            return self

        if self.parent_code is None:
            return None
        
        return self.parent_code.get_code_by_index(index-1)        
    
    def update_parent_code_by_index(self, index:int, new_code:'LinearCodeSearchRecord'):
        """
            0 is initial code
            1 is first parent code
            2 is second parent code
            ...
            last is itself
        """
        
        if index == self.parent_count-1:
            self.parent_code = new_code
            return
        
        if index == 0:
            return
        
        if self.parent_code is None:
            return 
        
        self.parent_code.update_parent_code_by_index(index, new_code)
    
    @staticmethod
    def from_json(q:int, json:Dict[str, Any]) -> 'LinearCodeSearchRecord':
        zero_code_str = f"[{json['min_distance']}, 0] linear code over GF({q})"
        if json["code"] != zero_code_str: 
            gen_matrix_record = GeneratorMatrixRecord.from_json(json["GenMatrix"])
            code:LinearCode = LinearCode(matrix(GF(q), gen_matrix_record.generator_matrix))
        else:
            # zero code
            code:LinearCode = LinearCode(matrix(GF(q), 0, json['min_distance']))
            
        code_params = LinearCodeSearchRecordParams(code, json["min_distance"], json['gen_objects'], json["const_method_params"])
        parent_code = None
        if "parent_code" in json and json["parent_code"] is not None:
            parent_code = LinearCodeSearchRecord.from_json(q, json["parent_code"])
                        
        return LinearCodeSearchRecord(parent_code, code, code_params)
        
class LinearCodeSearchRecordList:
    def __init__(self, records:Optional[List[LinearCodeSearchRecord] | Set[LinearCodeSearchRecord] | 'LinearCodeSearchRecordList'] = None):
        self.records:Dict[Tuple[int, int],LinearCodeSearchRecord] = {}
        if records is not None:
            self.update(records)

    def add(self, new_record:LinearCodeSearchRecord):
        key = (new_record.code_params.n, new_record.code_params.k)
        if key not in self.records:
            self.records[key] = new_record
            return
    
        record = self.records[key]
        if new_record.code_params.d > record.code_params.d:
            self.records[key] = new_record
            return
        
        if new_record.code_params.d == record.code_params.d:
            if new_record.parent_count < record.parent_count:
                self.records[key] = new_record
                return
    
    def update(self, new_records:'LinearCodeSearchRecordList' | Set[LinearCodeSearchRecord] | List[LinearCodeSearchRecord]):
        for record in new_records:
            self.add(record)
            
    def get(self, n:int, k:int) -> LinearCodeSearchRecord | None:
        key = (n, k)
        if key in self.records:
            return self.records[key]
        
        return None
    
    def __contains__(self, record:LinearCodeSearchRecord) -> bool:
        return record in self.records.values()
    
    def __iter__(self):
        return iter(self.records.values())
    
    def __len__(self):
        return len(self.records)
    
    def get_all(self) -> List[LinearCodeSearchRecord]:
        return list(self.records.values())
        
    
def apply_lemma_4_1_generate_best_possible_code(code_record:LinearCodeSearchRecord, max_iterations:int = 32):
    current_n = int(code_record.code.length())
    random_positions = random.sample(range(current_n), min(max_iterations, current_n))    
    new_codes = [lemma_4_1_generate_new_code_from(code_record.code, i) for i in random_positions]
    new_code, new_params, new_gen_objects = new_codes.pop()
    best_d = safe_minimum_distance(new_code)
    
    for (code, params, gen_objects) in new_codes:
        min_d = safe_minimum_distance(code)
        if min_d > best_d:
            new_code, new_params, new_gen_objects = code, params, gen_objects
            best_d = min_d
            
    code_params = LinearCodeSearchRecordParams(new_code, best_d, new_gen_objects, new_params)
    return LinearCodeSearchRecord(code_record, new_code, code_params)

def apply_theorem_4_3_generate_best_possible_code(code_record:LinearCodeSearchRecord, diff_n:int, diff_k:int, max_iterations:int = 8):   
    p = code_record.code.characteristic()

    def apply_theorem_4_3_generate_best_possible_code_once(code_record:LinearCodeSearchRecord, r:int):
        new_code, new_params,new_gen_objects = max([theorem_4_3_extended_const_method_generate_new_code_from(code_record.code, r) for _ in range(max_iterations)], key=lambda x: safe_minimum_distance(x[0]))
        best_d = safe_minimum_distance(new_code)
        
        code_params = LinearCodeSearchRecordParams(new_code, best_d, new_gen_objects, new_params)
        return LinearCodeSearchRecord(code_record, new_code, code_params)
    
    # not possible binary and ternary case
    if diff_n < p:
        raise Exception("Not possible to improve n by less than p")
    
    if diff_k < 0:
        raise Exception("Not possible to improve k by negative value")
           
    # diff_k = 1,
    if diff_k == 1:
        return apply_theorem_4_3_generate_best_possible_code_once(code_record, diff_n)

    #let diff_n = a*p + c where c < p since diff_n >=p, a at least 1
    a = diff_n//p
    c = diff_n%p        
    # at first n can be improved by p+c and k improved by 1
    next_code = apply_theorem_4_3_generate_best_possible_code_once(code_record, p + c)
    # k can be improved at most a-1 times and n can be improved by p
    for _ in range(a-1):
        next_code = apply_theorem_4_3_generate_best_possible_code_once(next_code, p)

    return next_code

def apply_theorem_4_7_generate_code(code_record:LinearCodeSearchRecord, m:int, r:int):
    new_code, new_params, new_gen_objects = theorem_4_7_generate_new_code_from(code_record.code, m, r, 8)
    new_code_d = safe_minimum_distance(new_code)
    
    code_params = LinearCodeSearchRecordParams(new_code, new_code_d, new_gen_objects, new_params)
    return LinearCodeSearchRecord(code_record, new_code, code_params)

def apply_prop_4_2_generate_generate_code(code_record:LinearCodeSearchRecord, r:int):
    new_code, new_params,new_gen_objects = prop_4_2_generate_new_code_from(code_record.code, r)
    new_code_d = safe_minimum_distance(new_code)
    
    code_params = LinearCodeSearchRecordParams(new_code, new_code_d, new_gen_objects, new_params)
    return LinearCodeSearchRecord(code_record, new_code, code_params)

def get_improved_code(target_n:int, target_k:int, target_d:int, code_record:LinearCodeSearchRecord):
    """
    Returns the appropriate construction method based on whether we want to
    improve code length (n), dimension (k), and/or minimum distance (d).

    Available methods and their effects:
    - lemma_4_1_generate_new_code_from: can improve d but lowers n and k
    - prop_4_2_generate_new_code_from: improves n, k stays same and d may stay same or improves
    - theorem_4_3_extended_const_method_generate_new_code_from: improves n by r and k by 1, d may change or stay same
    - theorem_4_7_generate_new_code_from: improves n by m and k by r but may lowers d
    """
    
    if target_n <0 or target_k < 0 or target_d < 0:
        raise Exception(f"Invalid target values {target_n}, {target_k}, {target_d}")
    
    p = code_record.code.characteristic()
    current_n = code_record.code_params.n
    current_k = code_record.code_params.k
    current_d = code_record.code_params.d
    
    diff_n = target_n - current_n
    diff_k = target_k - current_k
    
    should_improve_n = diff_n > 0
    should_improve_k = diff_k > 0
    should_improve_d = target_d > current_d
        
    # priority is always improving d
    if should_improve_d or diff_n <= 0 or diff_k <= 0:
        new_code = apply_lemma_4_1_generate_best_possible_code(code_record)
        if new_code.code_params.d >= target_d or new_code.code_params.d > current_d:
            return new_code, False
        
    if diff_n <= 0 or diff_k <= 0:
        return code_record, True

    # next priority is improving k it may lower d but we cannot do anything about it
    if should_improve_k:
        if diff_n >= p:
            return apply_theorem_4_3_generate_best_possible_code(code_record, diff_n, diff_k), False
        else:
            return apply_theorem_4_7_generate_code(code_record, diff_n, diff_k), False
        
    if should_improve_n:
        return apply_prop_4_2_generate_generate_code(code_record, diff_n), False
    
    return code_record, True

def kill_child_processes(parent_pid, sig=signal.SIGTERM):
    try:
        try:
            parent = psutil.Process(parent_pid)
        except psutil.NoSuchProcess:
            return
        children = parent.children(recursive=True)
        for process in children:
            process.send_signal(sig)
    except:
        pass

@cached_method
def get_n_d_lp_array(q:int) -> List[List[int]]:
    n_d_lp_array_raw:List[List[str]] = []
    if os.path.exists(f"outputs/LCD_ILP_output_{q}.csv"):
        with open(f"outputs/LCD_ILP_output_{q}.csv", 'r') as file:
            reader = csv.reader(file)
            n_d_lp_array_raw = list(reader) # type: ignore
    
    # rstrip * and up then convert to int
    n_d_lp_array = [[int(x.rstrip("*").rstrip('up')) for x in row] for row in n_d_lp_array_raw]
    return n_d_lp_array

def get_possible_d(q:int, n:int, k:int, n_d_lp_array:List[List[int]]) -> int | None:
    if k == 1:
        return n
    
    d_singleton = n -k +1

    # max int
    d_lp_array:int = sys.maxsize
    if len(n_d_lp_array) > n-1:
        row = n_d_lp_array[n-1]
        for d, k_lp in enumerate(row): # type: ignore
            try:
                if int(k_lp) <= k:
                    d_lp_array  = d
                    break
            except:
                pass
        
    d = KnownResults.get_largest_min_distance(q, n, k) # type: ignore
    if isinstance(d, int):
        return d
    
    if d_lp_array != sys.maxsize:
        return min(d_singleton, d_lp_array)
        
    return get_possible_d(q, n, k-1, n_d_lp_array)


def generate_best_code_for_nk(q:int, absolute_target_n: int, absolute_target_k: int, absolute_max_possible_d:int, initial_code_pool: List[LinearCodeSearchRecord],
                              max_iterations: int = 1000) -> Optional[LinearCodeSearchRecordSerialized]:
    """
    Try to generate (or improve) an LCD code [target_n, target_k, d] over GF(q).
    We'll do a BFS from a "closest" code, step by step,
    applying the 4 transformations until we reach (target_n, target_k).
    
    :param q: field size
    :param target_n: desired length
    :param target_k: desired dimension
    :param max_iterations: a safeguard to stop BFS if it grows too large
    :return: the best code found for (target_n, target_k) or None if not found
    """
    
    def get_deviated_codes(executor:ProcessPoolExecutor, target_n:int, target_k:int, deviation:int, code_pool:LinearCodeSearchRecordList):
        target_list = [(target_n + i, target_k + j) for i in range(-deviation, deviation + 1) for j in range(-deviation, deviation + 1) if target_k + j >0  and target_n + i > 0 and target_k + j <= target_n + i]
        improved_codes_set = LinearCodeSearchRecordList()

        features = []
        
        for _n, _k in target_list:
            for candidate in code_pool:
                max_possible_d = get_possible_d(q, _n, _k, get_n_d_lp_array(q)) 
                if max_possible_d is None:
                    max_possible_d = absolute_max_possible_d

                features.append(executor.submit(get_improved_code, _n, _k, max_possible_d, candidate))

        for feature in as_completed(features):
            try:
                improved_code, dead_end = feature.result()
                if not dead_end:
                    improved_codes_set.add(improved_code)
            except:
                traceback.print_exc()
                continue
                                                
        return improved_codes_set        
    
    def apply_deviated_codes(executor:ProcessPoolExecutor, target_n:int, target_k:int, deviation:int, code_pool:LinearCodeSearchRecordList) -> LinearCodeSearchRecordList:
        new_code_pool = get_deviated_codes(executor, target_n, target_k, deviation, code_pool)
        for i in range(1, deviation):
            next_deviated_codes = new_code_pool
            for d in range(deviation-i, 0, -1):                
                next_deviated_codes = get_deviated_codes(executor, target_n, target_k, d, next_deviated_codes)
                new_code_pool.update(next_deviated_codes)
            
        return new_code_pool
    
    # Prepare BFS queue form 
    queue:Deque[LinearCodeSearchRecord] = deque()
    
    # initial code pool as well
    queue.extend(initial_code_pool)
    visited:LinearCodeSearchRecordList = LinearCodeSearchRecordList(initial_code_pool)
    iterations = 0
    best_for_target:LinearCodeSearchRecord|None = None
    batch_size = 12
    
    with ProcessPoolExecutor(max_workers=12) as executor:
        queue.extend(apply_deviated_codes(executor, absolute_target_n, absolute_target_k, 3, LinearCodeSearchRecordList(initial_code_pool)))
        
        while queue and iterations < max_iterations:
            features = [executor.submit(get_improved_code, absolute_target_n, absolute_target_k, absolute_max_possible_d, queue.popleft()) for _ in range(min(batch_size, len(queue)))]
            
            for feature in as_completed(features):
                try:
                    iterations += 1

                    improved_code, dead_end = feature.result()

                    if improved_code.is_n_k_equal(absolute_target_n, absolute_target_k):
                        if best_for_target is None:
                            best_for_target = improved_code
                        
                        assert(best_for_target is not None)
                        if best_for_target.code_params.d == absolute_max_possible_d:
                            executor.shutdown(wait=False)
                            kill_child_processes(os.getpid())
                            return best_for_target.serialize()
                        
                        if improved_code.code_params.d >= best_for_target.code_params.d:
                            best_for_target = improved_code
                
                    if dead_end:
                        continue            
                    
                    if improved_code in visited:
                        continue
                    visited.add(improved_code)
                    queue.append(improved_code)
                except:
                    traceback.print_exc()
                    continue
        
    return best_for_target.serialize() if best_for_target is not None else None

def gen_objects_contains(code_record:LinearCodeSearchRecord, search:str) -> Tuple[LinearCodeSearchRecord, bool]:
    if search in code_record.code_params.gen_objects:
        return code_record, True
    if code_record.parent_code is not None:
        return gen_objects_contains(code_record.parent_code, search)
    return code_record, False

def fix_parameters_for_theorem_4_7(code_search_record:LinearCodeSearchRecord, m:int, r:int) -> LinearCodeSearchRecord:
    gen_matrix_by_rows = code_search_record.code.generator_matrix().rows()
    gen_matrix_by_columns = code_search_record.code.generator_matrix().columns()
    
    row_count = m
    # a is rxm matrix
    A = [list(gen_matrix_by_rows[i][:m]) for i in range(r)]
    X = [list(gen_matrix_by_rows[i][m:]) for i in range(r)]
    
    A_str = '\n'.join([str(A[i]).replace(',','') for i in range(len(A))])
    X_str = '\n'.join([str(X[i]).replace(',','') for i in range(len(X))])
    
    code_search_record.code_params.gen_objects = f"[{A_str}], [{X_str}]"
    
    return code_search_record

def apply_fix(code_search_record:LinearCodeSearchRecord):
    need_fix, found = gen_objects_contains(code_search_record, "dense matrix over Finite Field of size")
    if found:
        const_params = need_fix.code_params.construction_method
        m = int(const_params.split(",")[0].split("=")[1])
        r = int(const_params.split(",")[1].split("=")[1])
        if m <= 0 or r <= 0 or need_fix.parent_code is None:
            raise Exception(f"Invalid const params {const_params}")


        # improved = apply_theorem_4_7_generate_code(need_fix.parent_code, m, r)
        fixed_code = fix_parameters_for_theorem_4_7(need_fix, m, r)
        if code_search_record.parent_count > need_fix.parent_count:
            code_search_record.update_parent_code_by_index(need_fix.parent_count, fixed_code)
        else:
            code_search_record = fixed_code
        print(f"Fixed code {q}_{target_n}_{target_k}_{max_possible_d} with {m} and {r}")
        return code_search_record, True            
    
    return code_search_record, False
        

def find_closest_code(magma_session:Optional[MagmaSession], lcd_codes:Set[LinearCodeRecord], q:int, target_n:int, target_k:int, max_possible_d:int, output_file:File_Cache, thread_count=6, deviation:int = 5, max_codes_iteration:int = 512):
    keys = list(output_file.get_keys())
    
    for output_key in keys:
        if output_key.startswith(f"{q}_{target_n}_{target_k}") and output_file.contains(f"{q}_{target_n}_{target_k}_{max_possible_d}") == False:
            output = output_file.get(output_key)
            output_file.set(f"{q}_{target_n}_{target_k}_{max_possible_d}", output) # type: ignore
            output_file.remove(output_key)
            output_file.flush()
            print (f"Fixed max d found for {q}_{target_n}_{target_k}")
            break
    
    if output_file.contains(f"{q}_{target_n}_{target_k}_{max_possible_d}"):
        
        for _ in range(12):
            output_raw = output_file.get(f"{q}_{target_n}_{target_k}_{max_possible_d}")
            code_search_record = LinearCodeSearchRecord.from_json(q, output_raw)
            fixed_code, fixed = apply_fix(code_search_record)
            if fixed:
                output_file.set(f"{q}_{target_n}_{target_k}_{max_possible_d}", fixed_code.to_json())
        
        output_file.write()
                
    
    return 
    
    for output_key in output_file.get_keys():
        if output_key.startswith(f"{q}_{target_n}_{target_k}"):
            output = output_file.get(output_key)
            output_file.set(f"{q}_{target_n}_{target_k}_{max_possible_d}", output) # type: ignore
            output_file.remove(output_key)
            output_file.flush()
            print (f"Already found for {q}_{target_n}_{target_k}")
            return 
    
    
    # generate n,k list satisfying k <= n and n +- 4 and k +- 4 for q=2
    n_k_list = [(n, k) for n in range(target_n-deviation, target_n+(deviation + 1)) for k in range(1, n+1) if abs(n - target_n) <= deviation and abs(k - target_k) <= deviation]
    code_pool_raw = [min(lcd_codes, key=lambda code: abs(code.n - n) + abs(code.k - k)) for n,k in n_k_list ]
    # eliminate if multiple n, k, d    
    code_pool:LinearCodeSearchRecordList = LinearCodeSearchRecordList()
    for code in code_pool_raw:
        if code is not None:
            code_sage = code.to_sage_linear_code(magma_session)
            if not is_lcd_code(code_sage):
                raise Exception(f"Code {code_sage} is not LCD")
                
            if any([c.is_n_k_equal(code.n,code.k) and code.d == c.code_params.d for c in code_pool]):
                continue
            
            code_params = LinearCodeSearchRecordParams(code_sage, code.d, None, "Initial")
            code_pool.add(LinearCodeSearchRecord(None, code_sage, code_params))

    best_for_target:LinearCodeSearchRecord | None = None
    total_codes = len(code_pool)
    processed_codes = 0
     
    print(f"Total Codes: {total_codes}")
    
    with ProcessPoolExecutor(max_workers=thread_count) as executor:
        candidate_features=[executor.submit(generate_best_code_for_nk, q, target_n, target_k, max_possible_d, [code], max_codes_iteration) for code in code_pool]
                    
        try:
            for candidate_feature in as_completed(candidate_features):
                processed_codes += 1
                candidate_raw:LinearCodeSearchRecordSerialized|None = candidate_feature.result()
                
                candidate_d = candidate_raw.code_params.d if candidate_raw is not None else None

                print(f"Processed ({q} {target_n} {target_k} {max_possible_d}):{candidate_d} {processed_codes}/{total_codes} codes")
                
                if candidate_raw is None:
                    continue
                
                candidate = candidate_raw.to_linear_code_search_record()
                
                if candidate.is_n_k_equal(target_n, target_k):
                    if best_for_target is not None and candidate.code_params.d < best_for_target.code_params.d:
                        continue
                    
                    best_for_target = candidate
                    
                    if best_for_target.code_params.d == max_possible_d:
                        executor.shutdown(wait=False)
                        kill_child_processes(os.getpid())
                        break
            if best_for_target is not None:
                print(f"Improved Code: {best_for_target.code_params}") # type: ignore
                output_file.set(f"{q}_{target_n}_{target_k}_{max_possible_d}", best_for_target.to_json()) # type: ignore
                output_file.flush()
        except:
            print(traceback.format_exc())


def get_search_list(q:int, n_max:int, n_d_lp_array:List[List[int]]):
    search_list = []
    for n in range(q, n_max+1):
            for k in range(1, n+1):
                result = KnownResults.get_largest_min_distance(q, n, k)
                if result is None:
                    d = get_possible_d(q, n, k, n_d_lp_array)
                    search_list.append((q, n, k, d))
    return search_list

def code_list_to_latex(code_records:List[Tuple[bool, LinearCodeSearchRecord]]):
    latex_output = "\\begin{align*}\n"
    item = "&"
    code_per_item = 7
    for index, (max_possible_d_reached, code_record) in enumerate(code_records):    
        d = str(code_record.code_params.d)
        if max_possible_d_reached:
            d +='^*'
                
        code = f"[{code_record.code_params.n},\\ {code_record.code_params.k},\\ {d}]"
        item += code + ",\\ "
        if (index+1) % code_per_item == 0:
            latex_output += f"{item.rstrip(',\\ ')} \\\\\n"
            item = "&"
    
    if item != "&":
        latex_output += f"{item.rstrip(',\\ ')} \\\\\n"

    latex_output += "\\end{align*}"

    # copy to clipboard
    print(latex_output)

    import pyperclip
    pyperclip.copy(latex_output)

if __name__ == "__main__":
    
    #q = 2
    # target_n = 29
    # target_k = 11
    # max_possible_d = 10
    
    # target_n = 28
    # target_k = 17
    # max_possible_d = 6
    #search_list = [(2, 26, 15, 6), (2, 28, 17, 6), (2, 29, 11, 10)]
    q = 3
    n_max = 50
            
    search_list = sorted(get_search_list(q, n_max, get_n_d_lp_array(q)), key=lambda x: x[1])
    
    output_file = File_Cache(f"outputs/code_generation_{q}.json")
    
    #latex
    # n_k_list= []
    # for key in output_file.get_keys():
    #     code_raw = output_file.get(key)
    #     code_record = LinearCodeSearchRecord.from_json(q, code_raw)
        
    #     max_possible_d_reached = key == f"{q}_{code_record.code_params.n}_{code_record.code_params.k}_{code_record.code_params.d}"
    #     d = str(code_record.code_params.d)
    #     if max_possible_d_reached:
    #         d +='*'
        
    #     n_k_list.append((max_possible_d_reached, code_record))
    
    # c = len(n_k_list)//4
    
    # import numpy as np
    # n_k_list = list(sorted(n_k_list, key=lambda x: (x[1].code_params.n, x[1].code_params.k )))
    # n_array = np.array_split(n_k_list,4)
    
    # for batch in n_array:
    #     code_list_to_latex(list(batch))
    
    magma_session = None
    #magma_session = create_magma_session(12)
    #lcd_codes = get_lcd_codes_q(magma_session, q)
    lcd_codes = get_lcd_codes_q_excluding_quasi_cyclic(q)
    for q, target_n, target_k, max_possible_d in search_list:
        print(f"Searching for {q}, {target_n}, {target_k}, {max_possible_d}")
        find_closest_code(magma_session, lcd_codes, q, target_n, target_k, max_possible_d, output_file) 
    
    output_file.flush()
