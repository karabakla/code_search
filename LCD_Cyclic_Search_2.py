from concurrent.futures import ProcessPoolExecutor, as_completed
import os
from random import randint
from time import sleep
import traceback
from typing import Dict, Iterable, List, Tuple, Union
from KnownPaperResults import KnownResults
from Utils.Code_Utils import is_self_reciprocal_polynomial, to_monic_reciprocal_polynomial
from Utils.File_Cache import File_Cache
from Utils.Magma.BestDimensionLinearCode import BDLC, BDLCRecord
from Utils.Magma.MinumumDistance import CyclicCodeMinDistance
from Utils.Types import CyclicCodeRecord, LinearCodeRecord
from sage.all import PolynomialRing, FiniteField, gcd, Polynomial, prod, codes, magma, fork # type: ignore
import itertools

# PYDEVD_WARN_EVALUATION_TIMEOUT 
os.environ["PYDEVD_WARN_EVALUATION_TIMEOUT"] = "100000"

def should_skip_code(q:int, n:int, k:int) -> bool:
    known_result = KnownResults.get_largest_min_distance(q, n, k)
    if isinstance(known_result, int):
        return True
    if isinstance(known_result, str):
        return known_result.isdecimal()
    return False

def prepare_self_reciprocal_factors(m:int, q:int) -> List[Polynomial]:
    if gcd(m, q) != 1:
        raise ValueError("m must be coprime to the characteristic of the field.")
    
    Fq = FiniteField(q, 'w')
    P = PolynomialRing(Fq, 'x')
    x = P.gen()
    
    # Make it a hash set for fast look up, since we are sure that the factors are unique
    factors:set[Polynomial] = set([f.monic() for (f, _) in (x**m - 1).factor()]) # type: ignore
    
    # sperate the factors into two groups
    grouped_factors:Dict[str, Union[set[Polynomial], set[Tuple[Polynomial, Polynomial]]]] = {'self_recip':set(), 'recip_pairs':set()}
    
    while len(factors) > 0:
        p = factors.pop()
        if is_self_reciprocal_polynomial(p):
            grouped_factors['self_recip'].add(p)
        else:
            recip_proc = to_monic_reciprocal_polynomial(p)
            if recip_proc not in factors:
                continue # sanity check, skip the reciprocal polynomial if it is not in the factors
                            
            grouped_factors['recip_pairs'].add((p, recip_proc))
            factors.remove(recip_proc)
    
    all_recip_polynomials: set[Polynomial] = set()

    # itertools.product([0, 1], repeat=len(grouped_factors['self_recip'])) generates all possible combinations of 0 and 1 for the self reciprocal factors
    # example: if we have 3 self reciprocal factors, then the combinations will be [(0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), (1, 0, 0), (1, 0, 1), (1, 1, 0), (1, 1, 1)]
    for sr_mask in itertools.product([0, 1], repeat=len(grouped_factors['self_recip'])):
        for rp_mask in itertools.product([0, 1], repeat=len(grouped_factors['recip_pairs'])):
            # skip the empty combinations
            if sum(sr_mask) + sum(rp_mask) == 0:
                continue
            
            sr_comb = [f for i, f in enumerate(grouped_factors['self_recip']) if sr_mask[i]]
            rp_comb = [prod(recip_pair) for i, recip_pair in enumerate(grouped_factors['recip_pairs']) if rp_mask[i]]
            
            unique_combination = sr_comb + rp_comb

            new_recip_polynomial = prod(unique_combination)
            
            if new_recip_polynomial == x**m - 1 or new_recip_polynomial == 0:
                continue
            all_recip_polynomials.add(new_recip_polynomial)

    # test if all the factors are self reciprocal
    for f in all_recip_polynomials:
        if not is_self_reciprocal_polynomial(f):
            raise ValueError("Not all factors are self reciprocal")
    
    all_recip_polynomials_skipped = [f for f in all_recip_polynomials if not should_skip_code(q, m, m - f.degree())]
    return all_recip_polynomials_skipped # type: ignore


class BDLC_Provider:
    def __init__(self, bdlc_file_cache:File_Cache):
        self.bdlc_cache = bdlc_file_cache
        self.bdlc = BDLC()
        
        self.requested_codes:Dict[int, CyclicCodeRecord] = {}
        
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

    def put_request(self, cyclic_code:CyclicCodeRecord):
        if self.is_bdlc_cache_exist(cyclic_code.q, cyclic_code.n, cyclic_code.d):
            self.requested_codes[self.__get_self_next_unique_request_id__()] = cyclic_code
            return
        
        request_id = self.bdlc.put_request(BDLCRecord(cyclic_code.q, cyclic_code.n, cyclic_code.d))
        self.requested_codes[request_id] = cyclic_code

    def get_online_request_count(self):
        return self.bdlc.get_request_count()
    
    def get_request_count(self):
        return len(self.requested_codes)
    
    def get_results(self) -> List[Tuple[CyclicCodeRecord, LinearCodeRecord]]:
        results_pairs:List[Tuple[CyclicCodeRecord, LinearCodeRecord]] = []
        results = self.bdlc.get_results()
        
        for request_id in self.requested_codes.keys():
            lc:LinearCodeRecord | None = None
            requested_code = self.requested_codes[request_id]
            if request_id in results:
                lc = results[request_id]
                self.save_bdlc_code(lc)
            else:                
                lc = self.get_cached_bdlc_code(requested_code.q, requested_code.n, requested_code.d)        

            if lc is None:
                raise ValueError("Some unrecoverable error happened")
            
            results_pairs.append((requested_code, lc))
        
        self.requested_codes = {}
        return results_pairs

class CyclicCodeFileCache(File_Cache):
    def __init__(self, q:int, out_dir:str):
        super().__init__(os.path.join(out_dir, f"LCD_Cyclic_Codes_q{q}.json"))
        self.q = q
    
    def __get_key__(self, n, k, d):
        return f"LCD_Cyclic_Code_{self.q}_{n}_{k}_{d}"

    def save_cyclic_code(self, cyclicCode:CyclicCodeRecord):
        print(f"Saving: {cyclicCode}")
        key = self.__get_key__(cyclicCode.n, cyclicCode.k, cyclicCode.d)  
        
        # we already have one with the same key, just append the generator polynomial
        if self.contains(key):
            value = self.get(key)
            if f"{cyclicCode.gen_pol}" not in value['gen_pols']:
                value['gen_pols'].append(f"{cyclicCode.gen_pol}")
                self.set(key, value)
            return
        
        # first time we see this code
        self.set(key, {'n':int(cyclicCode.n), 'k': int(cyclicCode.k), 'd': int(cyclicCode.d), 'gen_pols':[f"{cyclicCode.gen_pol}"], 'is_lcd':cyclicCode.is_lcd })
    
    def get_cyclic_codes(self, n, k, d):
        key = self.__get_key__(n, k, d)
        value = self.get(key)
        Fq = FiniteField(self.q, 'w')
        P = PolynomialRing(Fq, 'x')
        return [CyclicCodeRecord(self.q, n, k, d, P(gen_pol), value['is_lcd']) for gen_pol in value['gen_pols']]      
    
    
def get_min_distance(cyclic_code:codes.CyclicCode) -> int:
    print(f"Min distance:{cyclic_code}, generator:{cyclic_code.generator_polynomial()}")
    # def get_min_distance_online_magma(C) -> int | None:        
    #     sleep(randint(1, 10)) # wait for a random time to avoid spamming the server
    #     return CyclicCodeMinDistance.get_min_distance(len(C.base_field()), C.length(), C.generator_polynomial())

    # magma_min_distance = get_min_distance_online_magma(cyclic_code)
    # if isinstance(magma_min_distance, int) and magma_min_distance > 0:
    #     return magma_min_distance
    
    magma.SetNthreads(64)
    magma_min_distance = magma.MinimumDistance(cyclic_code)
    if isinstance(magma_min_distance, int) and magma_min_distance > 0:
        return magma_min_distance
    
    return cyclic_code.minimum_distance(algorithm="guava")
    
def save_cyclic_cached_code(cached_code_file:File_Cache, cyclicCode:CyclicCodeRecord):
    key = f"{cyclicCode.q}_{cyclicCode.n}_{cyclicCode.gen_pol}"
    cached_code_file.set(key, cyclicCode.to_json())
    
def get_cached_cyclic_code(cached_code_file:File_Cache, q, n, gen_pol):
    if cached_code_file.contains(f"{q}_{n}_{gen_pol}"):
        cached_code = CyclicCodeRecord.from_json(cached_code_file.get(f"{q}_{n}_{gen_pol}"))
        if cached_code.d > 0:
            return cached_code
        
        print(f"Removing cache entry for {cached_code}")
        cached_code_file.remove(f"{q}_{n}_{gen_pol}")
        
    return None

def get_cyclic_codes(calculated_codes:File_Cache, factor:Polynomial, code_len:int) -> CyclicCodeRecord:
    cached_code = get_cached_cyclic_code(calculated_codes, len(factor.base_ring()), code_len, factor)
    if cached_code is not None:
        return cached_code
    
    cyclic_code = codes.CyclicCode(generator_pol=factor, length=code_len)
    n = code_len
    k = cyclic_code.dimension()
    d = get_min_distance(cyclic_code)
    q = len(cyclic_code.base_field())
    
    return CyclicCodeRecord(q, n, k, d, factor, True)


def handle_cyclic_code(cyclic_code:CyclicCodeRecord, linear_code:LinearCodeRecord, output_cache:CyclicCodeFileCache):
    if cyclic_code.q != linear_code.q:
        raise ValueError("q values do not match")
    
    # we requested for bdlc for n,d  but magma returned a different code then our code is best for given n,d
    if cyclic_code.n != linear_code.n or cyclic_code.d != linear_code.d:
        output_cache.save_cyclic_code(cyclic_code)
        return        

    # we have a better code
    if cyclic_code.k >= linear_code.k and not linear_code.is_lcd:
        output_cache.save_cyclic_code(cyclic_code)
        return

def handle_bdlc_results(bdlc_results:List[Tuple[CyclicCodeRecord, LinearCodeRecord]], output_cache:CyclicCodeFileCache):
    for cyclic_code, linear_code in bdlc_results:
        handle_cyclic_code(cyclic_code, linear_code, output_cache)


def main():
    m_max = 100
    m_min = 97
    q = 3
    m_q_array = [(m, q) for m in range(m_min, m_max+1) if gcd(m, q) == 1]
    
    bdlc_file_cache = File_Cache(f"Utils/Magma/BDLC_cache/bdlc_cache_q{q}.json")
    output_cache = CyclicCodeFileCache(q, "outputs")
    cached_codes = File_Cache(f"outputs/cache/CyclicCodes_cache_q{q}.json")

    
    bdlc_provider = BDLC_Provider(bdlc_file_cache)
    
    search_list_raw = [(prepare_self_reciprocal_factors(m, q), m) for m, q in m_q_array]
    search_list = [(factors ,m) for factors, m in search_list_raw if len(factors) > 0]
    search_list_flat = [(f, m) for factors, m in search_list for f in factors]
    
    total_tasks = len(search_list_flat)
    print(f"Total tasks: {total_tasks}")
    completed_tasks = 0

    with ProcessPoolExecutor(max_workers=1) as executor:
        try:
            cyclic_code_features=[executor.submit(get_cyclic_codes, cached_codes, f, m) for f,m in search_list_flat]
                    
            for cyclic_code_feature in as_completed(cyclic_code_features):
                
                completed_tasks += 1
                print(f"Completed tasks: {completed_tasks}/{total_tasks}")
                
                cyclic_code = cyclic_code_feature.result()                  
                            
                save_cyclic_cached_code(cached_codes, cyclic_code)
                
                bdlc_provider.put_request(cyclic_code)
                
                if bdlc_provider.get_online_request_count() < 100:
                    continue
                
                bdlc_results = bdlc_provider.get_results()
                handle_bdlc_results(bdlc_results, output_cache)
                
                # Don't spam the server
                sleep(100)

            if bdlc_provider.get_request_count() > 0:
                bdlc_results = bdlc_provider.get_results()
                handle_bdlc_results(bdlc_results, output_cache)
        except:
            print(traceback.format_exc())
        finally:
            bdlc_file_cache.close()
            output_cache.close()
            cached_codes.close()
                
if __name__ == "__main__":
    main()