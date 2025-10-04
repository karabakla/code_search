from collections import deque
from concurrent.futures import ProcessPoolExecutor, as_completed
import csv
from hmac import new
from itertools import repeat
import multiprocessing as mp
import os
import random
import traceback
from typing import Any, Callable, Deque, Dict, List, Optional, Set, Tuple, overload

from gurobipy import max_

from KnownPaperResults import KnownResults
from LCDCodePool.GetClosestLCD import get_lcd_codes_q, get_lcd_codes_q_excluding_quasi_cyclic
from Utils.File_Cache import File_Cache
from Utils.Code_Utils import safe_minimum_distance, zero_code
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

# common params for all code search records
class LinearCodeSearchRecordParams:
    def __init__(self, code:LinearCode, min_distance:Optional[int],  gen_objects:Any, construction_method:str):
        self.q:int = int(code.base_ring().order())
        self.n:int = int(code.length())
        self.k:int = int(code.dimension())
        self.d: int = int(min_distance) if min_distance is not None else int(safe_minimum_distance(code))
           
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
    
    def is_n_d_equal(self, n:int, d:int) -> bool:
        return self.code.length() == n and self.code_params.d == d
    
    def serialize(self) -> LinearCodeSearchRecordSerialized:
        return LinearCodeSearchRecordSerialized(self.parent_code, self)

    def to_linear_code_record(self) -> BdlcLcdCodeRecord:
        G = GeneratorMatrixRecord(self.code.generator_matrix()) # type: ignore
        return BdlcLcdCodeRecord(self.code_params.q, self.code_params.n, self.code_params.k, self.code_params.d, G)

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
        
    @staticmethod
    def from_json(q:int, json_data:Dict[str, Any]) -> 'LinearCodeSearchRecord':
        G_str = json_data["GenMatrix"] # type: ignore
        G = GeneratorMatrixRecord.from_json(G_str) # type: ignore
        
        code = zero_code(GF(q), int(json_data["min_distance"])) if G.n == 0 else LinearCode(matrix(GF(q), G.generator_matrix)) # type: ignore
        
        parent_code = None if json_data["parent_code"] is None else LinearCodeSearchRecord.from_json(q, json_data["parent_code"]) # type: ignore
        code_params = LinearCodeSearchRecordParams(code, json_data["min_distance"], json_data["gen_objects"], json_data["const_method_params"])
        record = LinearCodeSearchRecord(parent_code, code, code_params)
        record.parent_count = json_data["parent_count"] # type: ignore
        return record
                                                           
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


def apply_lemma_4_1_generate_best_possible_code(code_record:LinearCodeSearchRecord, target_d:int, return_if_d_bigger:bool) -> Tuple[LinearCodeSearchRecord, bool]:
    current_n = int(code_record.code.length())
    
    best_code = None
    
    for i in range(current_n):
        new_code, new_params, new_gen_objects = lemma_4_1_generate_new_code_from(code_record.code, i, code_record.code_params.d)
        if "skipped" in new_params:
            return code_record, True
          
        new_d = safe_minimum_distance(new_code)
        code_params = LinearCodeSearchRecordParams(new_code, new_d, new_gen_objects, new_params)
        best_code =  LinearCodeSearchRecord(code_record, new_code, code_params) if best_code is None or new_d > best_code.code_params.d else best_code
    
        if return_if_d_bigger and new_d >= target_d:
            return best_code, False
    
        if new_d == target_d:
            return best_code, False
        
    return best_code if best_code is not None else code_record, True
            

def apply_theorem_4_3_generate_best_possible_code(code_record:LinearCodeSearchRecord, diff_n:int, diff_k:int, target_d:int, max_iterations:int):   
    p = code_record.code.characteristic()

    def apply_theorem_4_3_generate_best_possible_code_once(code_record:LinearCodeSearchRecord, r:int):
        for _ in range(max_iterations):
            new_code, new_params,new_gen_objects = theorem_4_3_extended_const_method_generate_new_code_from(code_record.code, r)
            best_d = safe_minimum_distance(new_code)
            if best_d == target_d:
                code_params = LinearCodeSearchRecordParams(new_code, best_d, new_gen_objects, new_params)
                return LinearCodeSearchRecord(code_record, new_code, code_params)
        
        return code_record
    
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

def apply_theorem_4_7_generate_code(code_record:LinearCodeSearchRecord, m:int, r:int, target_d:int, max_iterations:int):
    new_code, new_params, new_gen_objects = theorem_4_7_generate_new_code_from(code_record.code, m, r, max_iterations, target_d)
    new_code_d = safe_minimum_distance(new_code)
    
    code_params = LinearCodeSearchRecordParams(new_code, new_code_d, new_gen_objects, new_params)
    return LinearCodeSearchRecord(code_record, new_code, code_params)

def apply_prop_4_2_generate_generate_code(code_record:LinearCodeSearchRecord, r:int):
    p = code_record.code.base_ring().characteristic()
    m = r-1        
    
    if not p.divides(m*(1+m)):
        return code_record

    new_code, new_params,new_gen_objects = prop_4_2_generate_new_code_from(code_record.code, r)
    new_code_d = safe_minimum_distance(new_code)
    
    code_params = LinearCodeSearchRecordParams(new_code, new_code_d, new_gen_objects, new_params)
    return LinearCodeSearchRecord(code_record, new_code, code_params)

def get_improved_code_exact_d(target_n:int, target_k:int, target_d:int, code_record:LinearCodeSearchRecord) -> LinearCodeSearchRecord:
    next_code = code_record
    count= 0
    for _ in range(500):
        prev_code = next_code
        next_code = get_improved_code_exact_d_imp(target_n, target_k, target_d, next_code)
        if next_code.code_params.n == target_n and next_code.code_params.k >= target_k and next_code.code_params.d == target_d:
            return next_code
        
        if next_code == prev_code:
            count += 1
            if count >= 5:
                print (f"No further improvement for {code_record.code_params} -> {next_code.code_params}")
                return next_code

    print(f"Max iterations reached for {code_record.code_params} -> {next_code.code_params}")
    return next_code
    
def get_improved_code_exact_d_imp(target_n:int, target_k:int, target_d:int, code_record:LinearCodeSearchRecord) -> LinearCodeSearchRecord:
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
      
    max_iteration = 500
         
    new_code = code_record
    
    def diff_k() -> int:
        return target_k - new_code.code_params.k
    
    def diff_n() -> int:
        return target_n - new_code.code_params.n
    
    def should_improve_n() -> bool:
        return diff_n() > 0
    
    def should_improve_k() -> bool:
        return diff_k() > 0
    
    def should_improve_d() -> bool:
        return new_code.code_params.d < target_d
    
    if should_improve_d() or not should_improve_n():
        new_code, _ = apply_lemma_4_1_generate_best_possible_code(new_code, target_d, False)
        
    if should_improve_k() and diff_n() >= p:
        new_code = apply_theorem_4_3_generate_best_possible_code(new_code, diff_n(), diff_k()+1, target_d, max_iteration)

    if should_improve_n():
        new_code = apply_prop_4_2_generate_generate_code(new_code, diff_n())
        
    if should_improve_k():
        new_code = apply_theorem_4_7_generate_code(new_code, max(diff_n(), 0), diff_k()+1, target_d, max_iteration)
         
    return new_code

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

def exact_code_generation_favor_d(q:int, n:int, k:int, d:int, lcd_codes:Set[LinearCodeRecord], output_file:File_Cache):
    print(f"Searching for {q}, {n}, {k}, {d}")
    
    code_pool:LinearCodeSearchRecordList = LinearCodeSearchRecordList()
    for code in lcd_codes:
        if code is not None:
            code_sage = code.to_sage_linear_code(None)
            if not is_lcd_code(code_sage):
                raise Exception(f"Code {code_sage} is not LCD")
                
            code_params = LinearCodeSearchRecordParams(code_sage, code.d, None, "Initial")
            code_pool.add(LinearCodeSearchRecord(None, code_sage, code_params))
    
    with ProcessPoolExecutor(max_workers=12) as executor:
        improved_code = [executor.submit(get_improved_code_exact_d, n, k, d, c) for c in code_pool]
        for feature in as_completed(improved_code):
            try:
                next_code = feature.result()
                if not is_lcd_code(next_code.code):
                    print(f"Generated code is not LCD {next_code.code}")
                    continue
                
                if next_code.is_n_d_equal(n, d) and next_code.code_params.k >= k:
                    print(f"Found Code: {next_code.code_params}") # type: ignore
                    output_file.set(f"{q}_{n}_{k}_{d}", next_code.to_linear_code_record().to_json()) # type: ignore
                    output_file.flush()
                    executor.shutdown(wait=False)
                    kill_child_processes(os.getpid())
                    return
            except:
                traceback.print_exc()
                continue

def get_lcd_code_pool(q:int, n_max:int = 100) -> List[List[Set[BdlcLcdCodeRecord]]]:
    lcd_codes = get_lcd_codes_q_excluding_quasi_cyclic(q)
    
    n_d_code_list: List[List[Set[BdlcLcdCodeRecord]]] = [ [ set() for _ in range(n_max+1)] for _ in range(n_max+1)]
    
    for lcd_code in lcd_codes:
        n = lcd_code.n
        d = lcd_code.d
        k = lcd_code.k
        if n <= n_max:
            n_d_code_list[n][d].add(lcd_code) # type: ignore
    
    output_file = File_Cache(f"outputs/code_generation_q{q}.json")
    
    def flatten_code(code_record:LinearCodeSearchRecord) -> List[LinearCodeSearchRecord]:
        if code_record.parent_code is None:
            return []
        return [code_record, *flatten_code(code_record.parent_code)]
    
    for key in output_file.get_keys():
        code_record = LinearCodeSearchRecord.from_json(q, output_file.get(key)) # type: ignore
        for code in flatten_code(code_record):
            n = code.code_params.n 
            d = code.code_params.d
            k = code.code_params.k
            q = code.code_params.q
            G = GeneratorMatrixRecord(code.code.generator_matrix()) # type: ignore
            if n <= n_max:
                n_d_code_list[n][d].add(BdlcLcdCodeRecord(q, n, k, d, G)) # type: ignore
        
    return n_d_code_list

def should_skip(q:int, n:int, d:int):
    return KnownResults.get_upper_bound_dimension_explicit(q, n, d) is not None

if __name__ == "__main__":    
    q =2
    
    n_d_code_list = get_lcd_code_pool(q,70)
    
    output_file = File_Cache(f"outputs/code_generation_complete_q{q}.json")
        
    list_search_entries = []
    
    for n in range(0,70):
        for d in range(1, n+1):
            if should_skip(q, n, d):
                continue
            
            current_k = max(n_d_code_list[n][d], key=lambda x: x.k, default=None) # type: ignore
            
            if any(output_file.contains(f"{q}_{n}_{k}_{d}") for k in range(0, n+1)):
                continue
            
            if current_k is None:
                continue
            
            if output_file.contains(f"{q}_{n}_{current_k.k}_{d}"):
                print(f"Skipping {q}, {n}, {current_k.k}, {d} since already exists")
                continue
            
            next_candidates = [item for n_search in range(n-2, n+1) for next_d in range(d, n+1) for item in n_d_code_list[n_search][next_d]]
            next_k = max(next_candidates, key=lambda x: x.k, default=None) # type: ignore
            
            if next_k is None:
                continue
            
            if next_k.k > current_k.k:
                list_search_entries.append((current_k.n, next_k.k, current_k.d))
                print(f"Found possible improvement {current_k.n}, {current_k.k}, {current_k.d} -> {current_k.n}, {next_k.k}, {current_k.d}")
                continue
            
            output_file.set(f"{q}_{current_k.n}_{current_k.k}_{current_k.d}", current_k.to_json())
    
    output_file.flush()

    print(f"Total search entries: {len(list_search_entries)}")
    for index, entry in enumerate(list_search_entries):
        target_n, target_k, target_d = entry
        lcd_codes = set()
        for n in range(target_n-15, target_n+15):
            for d in range(target_d-15, target_d+15):
                for k in range(0, n+1):
                    if output_file.contains(f"{q}_{n}_{k}_{d}"):
                        try:
                            code_from_output = BdlcLcdCodeRecord.from_json(output_file.get(f"{q}_{n}_{k}_{d}")) # type: ignore
                            if not is_lcd_code(code_from_output.to_sage_linear_code(None)):
                                raise Exception(f"Code {code_from_output} is not LCD")
                            lcd_codes.add(code_from_output) # type: ignore
                        except Exception as e:
                            pass                           

                for code in n_d_code_list[n][d]:
                    lcd_codes.add(code) # type: ignore
                
        print(f"Starting search for {q}, {target_n}, {target_k}, {target_d} with {len(lcd_codes)} LCD codes")
        exact_code_generation_favor_d(q, target_n, target_k, target_d, lcd_codes, output_file) # type: ignore
        print(f"Completed search for {q}, {target_n}, {target_k}, {target_d} ({index+1}/{len(list_search_entries)})")
