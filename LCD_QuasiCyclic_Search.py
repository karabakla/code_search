# Sage equivalent of the Magma code

import time
from typing import Dict, Tuple, Set
from concurrent.futures import ProcessPoolExecutor, as_completed
import os
import re
import traceback
from typing import List, TypeVarTuple
from unittest import result
from KnownPaperResults import KnownResults
from Utils.MagmaUtils import MagmaSession
from Utils.Types import CyclicCodeRecord, LinearCodeRecord, QuasiCyclicCodeRecord
from sage.all import * # type: ignore
from sage.coding.linear_code import LinearCode # type: ignore
from sage.coding.cyclic_code import * # type: ignore
from sage.misc.prandom import randrange # type: ignore
from sage.coding.code_constructions import random_linear_code # type: ignore

from Utils.File_Cache import File_Cache
from Utils.Magma.BestDimensionLinearCode import BDLC, BDLCRecord
from Utils.Code_Utils import  is_self_reciprocal_polynomial, root_of_unity, safe_minimum_distance, vertical_concatanate_codes, intersection_code, is_hermitian_LCD_code


# Load the magma specific code and run the session
def create_magma_session(thread_count = 1):
    magma_session = MagmaSession(f"{os.getcwd()}/Utils/Magma/MagmaCodes", thread_count)
    magma_session.magma.set_seed(1)
    return magma_session

class LCD_QC_Search:
    def __init__(self, q, m, n, magma_session):
        self.magma_session:MagmaSession = magma_session
        self.magma = magma_session.magma
        self.q:int = q
        self.m:int = m
        self.n:int = n
        
        self.Fq = GF(self.q, 'w')
        self.w = self.Fq.primitive_element()
        self.F_ext = self.magma.Parent(self.magma.RootOfUnity(m, self.Fq))
        #self.F_ext = root_of_unity(m, self.Fq).parent()
        self.P = PolynomialRing(self.Fq, 'x')
        self.x = self.P.gen()

        # Factor the polynomial x^m - 1
        self.F = self.P(self.x**m - 1).factor()
        self.s = len(self.F)
        self.Factors = [f[0] for f in self.F]

        # Reorder the sequence of irreducible factors such that the reciprocal
        # of Factors[j] equals either Factors[j] or Factors[j+1]
        for j in range(self.s):
            recip = self.Factors[j].reverse().monic()
            
            if self.Factors[j] != recip:
                for r in range(j + 1, self.s):
                    if self.Factors[r] == recip:
                        self.Factors[j + 1], self.Factors[r] = self.Factors[r], self.Factors[j + 1]
                        break

        # Get the sequence of degrees of the factors
        self.Deg = [f.degree() for f in self.Factors]

        # Construct the sequence of extension fields
        self.Ext = [GF(self.q**self.Deg[i], 'w%d' % i) for i in range(self.s)]

        # magma code: L_alpha:=[Roots(f,F_ext)[1,1]: f in Factors];

        #L_alpha  = [f.roots(F_ext)[0][0] for f in Factors]

        self.L_alpha=[self.magma.Roots(f,self.F_ext)[1,1] for f in self.Factors]

        # ensure that the selected roots are reciprocals of each other
        for i in range(1, len(self.Factors)):
            if self.Factors[i] == self.Factors[i - 1].reverse().monic():
                self.L_alpha[i] = 1 / self.L_alpha[i - 1]

        self.SelfRecipFactorTest = [is_self_reciprocal_polynomial(f) for f in self.Factors]
                
    def is_reciprocal(self, index):
        return self.SelfRecipFactorTest[index]
    
    def get_degree(self, index):
        return self.Deg[index]
    
    def generate_random_code(self, index, max_try = 10):
        random_k = randrange(1, self.n)
              
        if self.is_reciprocal(index):
            if self.get_degree(index) == 1:
                return self.magma.GenerateRandomLCDCode(self.Ext[index], self.n, random_k, max_try), None
            else:
                return self.magma.GenerateRandomHermDualCode(self.Ext[index], self.n, random_k, max_try), None
        else:
            C1, C2 = self.magma.GenerateLinearCodeReciprocalPairs(self.Ext[index], self.n, random_k, max_try,  nvals = 2)
            return C1, C2
    
    def generate_random_code_list(self, max_try = 10):
        k = 0
        Cons = []
        while k < self.s:
            C1, C2 = self.generate_random_code(k, max_try)
            Cons.append(C1)
            k += 1
            if C2 is not None:
                Cons.append(C2)
                k += 1
                
        return Cons
    
    def generate_random_qc_code(self, max_try = 10) -> Tuple[Unknown, bool]:  # type: ignore
        Cons = self.generate_random_code_list(max_try)
                
        C = [self.magma.TraceExpansionCode(Cons[i], self.Fq, self.m, self.L_alpha[i]) for i in range(self.s)]
        QC = self.magma.CombineCodes(C)
        is_lcd = str(self.magma.IsLCDCode(QC)).lower() == "true"
        
        return QC, is_lcd # type: ignore
    
    def should_skip(self, code_len, code_dim):
        #return False
        
        # if self.q == 2:
        #     # skip the known cyclic codes
        #     if code_dim <= 5 or code_dim >= code_len - 6: 
        #         return True
        # if self.q == 3:
        #     # skip the known cyclic codes
        #     if code_dim < 3 or code_dim >= code_len - 5: 
        #         return True
        # return False
        
        known_result = KnownResults.get_largest_min_distance(self.q, code_len, code_dim)
        if isinstance(known_result, int):
            return True
        if isinstance(known_result, str):
            return known_result.isdecimal()
        return False
        
    
    def _parse_magma_QC_code_parameters_string(self, QC) -> LinearCodeRecord:
        # [27, 15, 4] Linear Code over GF(2)
        QC_str = str(QC)
        prams = QC_str.split("]")[0].split("[")[1].split(", ")
        n = int(prams[0])
        k = int(prams[1])
        d = -1
        if len(prams) < 3:
            while True:
                try:
                    d = int(self.magma.MinimumDistance(QC))
                    break
                except:
                    pass
        else :
            d = int(prams[2])
            
        return LinearCodeRecord(self.q, n, k, d)        
        
    
    def generate_random_none_zero_qc_record(self, max_try = 10):      
        for _ in range(max_try):
            QC, is_lcd = self.generate_random_qc_code()
            parsed_code = self._parse_magma_QC_code_parameters_string(QC)
            if parsed_code is None or parsed_code.is_zero_code() or self.should_skip(parsed_code.n, parsed_code.k):
                continue
            
            if not is_lcd:
                print("Code not LCD")
                continue
            
            # qc_degree = -1
            # try :
            #     qc_degree = int(str(QC).split("Quasi-cyclic of degree")[1].split("Linear")[0].strip())
            # except:
            #     try :
            #         for _ in range(10):
            #             try:
            #                 isQC, qc_degree = self.magma.myIsQuasiCyclic(QC, nvals = 2)
            #                 if str(isQC).lower() == "true" and int(qc_degree) != -1:
            #                     break
            #             except:
            #                 pass
            #     except:
            #         qc_degree = -1
            
            # if not isinstance(qc_degree,int):
            #     qc_degree = -1
            qc_degree = -1
            
            qc_gen_pol = str(self.magma.GeneratorPolynomialMatrix(QC)).replace("\n", ", ")
            # dim = int(self.magma.Dimension(QC))
            # min_dist = int(self.magma.MinimumDistance(QC))
            new_qc_record = QuasiCyclicCodeRecord(self.q, parsed_code.n, parsed_code.k, parsed_code.d, qc_gen_pol, qc_degree, is_lcd)
            return new_qc_record
        
        return None
    
    def is_zero_code(self, C):
        return self.magma.IsZeroCode(C)


class BDLC_Provider:
    def __init__(self, bdlc_file_cache:File_Cache):
        self.bdlc_cache = bdlc_file_cache
        self.bdlc = BDLC()
        
        self.requested_codes:List[QuasiCyclicCodeRecord] = []
        self.requested_unique_codes:Dict[BDLCRecord, int] = {}
        
        self.self_unique_request_id = 10_000_000
        
    def __get_self_next_unique_request_id__(self):
        self.self_unique_request_id += 1
        return self.self_unique_request_id
    
    def __get_key__(self, q, n, d):
        return f"Dim_BDLC_{q}_{n}_{d}" 

    def save_bdlc_code(self, lc:LinearCodeRecord):
        self.bdlc_cache.set(self.__get_key__(lc.q,lc.n,lc.d), lc.to_json())

    def is_bdlc_cache_exist(self, q, n, d):
        return self.bdlc_cache.contains(self.__get_key__(q,n,d))

    def get_cached_bdlc_code(self, q, n, d) -> LinearCodeRecord:
        return LinearCodeRecord.from_json(self.bdlc_cache.get(self.__get_key__(q,n,d)))        

    def put_request(self, quasi_cyclic_code:QuasiCyclicCodeRecord):
        if not self.is_bdlc_cache_exist(quasi_cyclic_code.q, quasi_cyclic_code.n, quasi_cyclic_code.d):
            request = BDLCRecord(quasi_cyclic_code.q, quasi_cyclic_code.n, quasi_cyclic_code.d)
            request_id = self.bdlc.put_request(request)    
            self.requested_unique_codes[request] = request_id
                    
        self.requested_codes.append(quasi_cyclic_code)

    def get_online_request_count(self):
        return self.bdlc.get_request_count()
    
    def get_request_count(self):
        return len(self.requested_codes)
    
    def get_results(self) -> List[Tuple[QuasiCyclicCodeRecord, LinearCodeRecord]]:
        results_pairs:List[Tuple[QuasiCyclicCodeRecord, LinearCodeRecord]] = []
        results = self.bdlc.get_results()
        
        for requested_code in self.requested_codes:
            request = BDLCRecord(requested_code.q, requested_code.n, requested_code.d)
            if request in self.requested_unique_codes:
                request_id = self.requested_unique_codes[request]
                if request_id in results:
                    lc = results[request_id]
                    self.save_bdlc_code(lc)
                    results_pairs.append((requested_code, lc))
            else:
                lc = self.get_cached_bdlc_code(requested_code.q, requested_code.n, requested_code.d)
                if lc is None:
                    raise ValueError("Some unrecoverable error happened")
                
                results_pairs.append((requested_code, lc))

        self.bdlc_cache.flush()
        
        self.requested_codes = []
        self.requested_unique_codes = {}
        return results_pairs


def parse_generator_poly_matrix_string(input_string:str):
     # Remove the outer square brackets and leading/trailing whitespace
    input_string = input_string.strip('[] ')
    
    # Split the string into rows based on '], ['
    rows = re.split(r'\], \[', input_string)
    
    # Define a regex pattern to match entire mathematical expressions
    pattern = r'[^\s]+(?:\s+\+\s+[^\s]+)*'
    
    # Parse each row using the regex pattern
    parsed_matrix = []
    for row in rows:
        for i in range(20):
            row  = row.replace(f'w{i}', 'x')
        
        elements = re.findall(pattern, row.strip())
        parsed_matrix.append(elements)
    
    return parsed_matrix

def save_quasi_cyclic_code(qc_Code:QuasiCyclicCodeRecord, output_cache:File_Cache):
    print(f"Saving: {qc_Code}")
    
    key = f"LCD_quasi_Cyclic_Code_{qc_Code.q}_{qc_Code.n}_{qc_Code.k}_{qc_Code.d}"  
    
    # we already have one with the same key, just append the generator polynomial
    gen_pol = f"{parse_generator_poly_matrix_string(qc_Code.gen_pol_matrix_str)}"
    if output_cache.contains(key):
        value = output_cache.get(key)
        if gen_pol not in value['gen_pols']:
            value['gen_pols'].append(gen_pol)
            output_cache.set(key, value)
            output_cache.flush()
        return
    
    # first
    output_cache.set(key, {'q':int(qc_Code.q), 'n':int(qc_Code.n), 'k': int(qc_Code.k), 'd': int(qc_Code.d), 'is_lcd':qc_Code.is_lcd, 'gen_pols':[gen_pol] })
    output_cache.flush()

def handle_bdlc_seach(qc_Code:QuasiCyclicCodeRecord, bdlc:LinearCodeRecord, output_cache:File_Cache):       
    if qc_Code.q != bdlc.q:
        raise ValueError("q values do not match")
    
    # we requested for bdlc for n,d  but magma returned a different code then our code is best for given n,d
    if qc_Code.n != bdlc.n or bdlc.d != bdlc.d:
        save_quasi_cyclic_code(qc_Code, output_cache)
        return        

    # we have a better code
    if qc_Code.k >= bdlc.k and not bdlc.is_lcd:
        save_quasi_cyclic_code(qc_Code, output_cache)
        return
        
# Start generating random quasi-cyclic codes
def run_generate_random_qc_code(iterate_count, q, m, n, magma_session = None) -> set[QuasiCyclicCodeRecord]:
    try:
        if magma_session is None:
            magma_session = create_magma_session(4)
        
        search = LCD_QC_Search(q, m, n, magma_session)
        results:set[QuasiCyclicCodeRecord] = set()
        for _ in range(iterate_count):
            #print(f"Generating: {m}, {n}")
            new_qc_record = search.generate_random_none_zero_qc_record(max_try=10)
            if new_qc_record is None:
                continue
            #print(f"Generated: {new_qc_record}")
            results.add(new_qc_record)
        
        print(f"Generated: {m}, {n}, {len(results)}")
        return results
    except:
        print(f"Error: Unknown", traceback.format_exc())
        return set()


def process_bdlc_results(bdlc_provider:BDLC_Provider, output_cache:File_Cache):
    bdlc_results = bdlc_provider.get_results()
    for echo_qc_code, bdlc in bdlc_results:
        handle_bdlc_seach(echo_qc_code, bdlc, output_cache)

def should_skip(q, m, n):
    code_len = m * n
    
    if q == 2 and code_len < 25:
        return True
        
    if q == 3 and code_len < 20:
        return True
    
    return False
    

def create_search_list(q, m_min, m_max, n_min, n_max):
    #m_n_list = [ (m, n) for m in range(m_min, m_max) if gcd(m, q) == 1 for n in range(n_min, n_max//m)]
    m_n_list = []
    for m in range(m_min, m_max):
        if gcd(m, q) != 1:
            continue
        for n in range(n_min, n_max//m):
            if should_skip(q, m, n):
                continue
            if (m, n) not in m_n_list:
                m_n_list.append((m, n))
            
    return m_n_list

def main():
    
# kill all magma processes
    os.system("killall magma.exe")
    
    q = 2
    iteration_count = 1000
    sch_count = 4
    m_n_list = create_search_list(q, 2, 36, 2, 115) #-> q :2
    #m_n_list = create_search_list(q, 2, 32, 2, 40)
    set_random_seed(1)
    
    bdlc_file_cache = File_Cache(f"Utils/Magma/BDLC_cache/bdlc_cache_q{q}.json", buffer_count=500)
    output_cache = File_Cache(f"outputs/LCD_QuasiCyclic_Codes_q{q}.json")

    bdlc_provider = BDLC_Provider(bdlc_file_cache)
    
    with ProcessPoolExecutor(max_workers=sch_count, max_tasks_per_child=1) as executor:
        futures = [executor.submit(run_generate_random_qc_code, iteration_count, q, m, n) for m, n in m_n_list]
        total = len(futures)
        count = 0

        for future in as_completed(futures):
            try:
                results:set[QuasiCyclicCodeRecord] = future.result()
                count += 1
                print(f"Completed: {count}/{total}")
                
                for result in results:
                    if bdlc_provider.is_bdlc_cache_exist(result.q, result.n, result.d):
                        cached_bdlc = bdlc_provider.get_cached_bdlc_code(result.q, result.n, result.d)
                        handle_bdlc_seach(result, cached_bdlc, output_cache)
                        continue
                    if bdlc_provider.get_online_request_count() >= 100:
                        process_bdlc_results(bdlc_provider, output_cache)

                    bdlc_provider.put_request(result)

                if bdlc_provider.get_online_request_count() >= 100:
                    process_bdlc_results(bdlc_provider, output_cache)
 

            except Exception:
                print(f"Error processing future: {traceback.format_exc()}")
        
        if bdlc_provider.get_request_count() >= 0:
                    process_bdlc_results(bdlc_provider, output_cache)
                    
if __name__ == '__main__':
    main()