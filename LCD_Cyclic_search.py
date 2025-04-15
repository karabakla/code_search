from concurrent.futures import ProcessPoolExecutor, as_completed
from time import sleep
from joblib import Parallel, delayed
#import sys; sys.path.append('/home/karabakla/sage/src')

from Utils.Code_Utils import is_LCD_code
from Utils.Magma.MinumumDistance import CyclicCodeMinDistance
from Utils.Types import CyclicCodeRecord, LinearCodeRecord
from sage.all import *

from Utils.File_Cache import File_Cache
from Utils.Magma.BestDimensionLinearCode import BDLC

os.environ["CYSIGNALS_CRASH_NDEBUG"]="yes"
os.environ['OMP_NUM_THREADS'] = '480'  
os.environ["SAGE_NUM_THREADS"] = '480'
m_max = 100
m_min = 3
q = 2
m_q_array = [ (m, q) for m in range(m_min, m_max+1) if gcd(m, q) == 1]

bdlc_file_cache = File_Cache(f"Utils/Magma/BDLC_cache/bdlc_cache_q{q}.json")
output_cache = File_Cache(f"outputs/LCD_Cyclic_Codes_q{q}.json")

calculated_codes = File_Cache(f"outputs/CyclicCodes_cache_q{q}.json")

bdlc_provider = BDLC()

def save_cyclic_calculated_code(cyclicCode:CyclicCodeRecord):
    key = f"{cyclicCode.q}_{cyclicCode.n}_{cyclicCode.gen_pol}"
    calculated_codes.set(key, cyclicCode.to_json())
    
def get_cached_calculeted_cyclic_code(q, n, gen_pol):
    if calculated_codes.contains(f"{q}_{n}_{gen_pol}"):
        return  CyclicCodeRecord.from_json(calculated_codes.get(f"{q}_{n}_{gen_pol}"))
    return None

def should_skip(q, code_len, factor):
    return False
    code_dim = code_len - factor.degree()
    if q == 2:
        # skip the known cyclic codes
        if code_dim <= 5 or code_dim >= code_len - 5: 
            return True
    if q == 3:
        # skip the known cyclic codes
        if code_dim <= 4 or code_dim >= code_len - 4: 
            return True
    return False

def prepare_factors(m, q):
    # Define the finite field and polynomial ring
    Fq = GF(q, name='w')
    P = PolynomialRing(Fq, 'x')
    x = P.gen()

    # Factor x^m - 1
    F = (x**m - 1).factor()
    s = len(F)
    Factors = [F[i][0] for i in range(s)]

    # Reorder the sequence of irreducible factors
    for j in range(s):
        recip = Factors[j].reverse().monic()  # Normalize(ReciprocalPolynomial(Factors[j]))

        if Factors[j] != recip:
            for r in range(j+1, s):
                if Factors[r] == recip:
                    Factors[j+1], Factors[r] = Factors[r], Factors[j+1]
                    break

    # Subset creation
    def SubSeq(S):
        Subsets = []
        for k in range(1, 2**len(S)):
            K = bin(k)[2:].zfill(len(S))
            INDEX = [r for r in range(len(K)) if K[r] == '1']
            Sub = [S[i] for i in INDEX]
            Subsets.append(Sub)
        return Subsets

    # Create all possible factors of x^m - 1
    AllFactors = []
    for subseq in SubSeq(Factors):           
        AllFactors.append(prod(subseq)) 

    # Isolate the self-reciprocal ones
    AllSelfRecipFactors = []
    for f in AllFactors:
        if f == f.reverse().monic():
            AllSelfRecipFactors.append(f)

    # Exclude x^m - 1
    AllSelfRecipFactors = [f for f in AllSelfRecipFactors if f != x**m - 1 and should_skip(q, m, f) is False]
    
    return AllSelfRecipFactors , m

def save_cyclic_code(cyclicCode:CyclicCodeRecord, is_LCD):
    key = f"LCD_Cyclic_Code_{cyclicCode.q}_{cyclicCode.n}_{cyclicCode.k}_{cyclicCode.d}"  
    
    # we already have one with the same key, just append the generator polynomial
    if output_cache.contains(key):
        value = output_cache.get(key)
        if f"{cyclicCode.gen_pol}" not in value['gen_pols']:
            value['gen_pols'].append(f"{cyclicCode.gen_pol}")
            output_cache.set(key, value)
        return
    
    # firs
    output_cache.set(key, {'n':int(cyclicCode.n), 'k': int(cyclicCode.k), 'd': int(cyclicCode.d), 'gen_pols':[f"{cyclicCode.gen_pol}"] })

def save_bdlc_code(lc:LinearCodeRecord):
    bdlc_file_cache.set(f"Dim_BDLC_{lc.q}_{lc.n}_{lc.d}", lc.k)

def is_bdlc_cache_exist(q, n, d):
   return bdlc_file_cache.contains(f"Dim_BDLC_{q}_{n}_{d}")

def get_cached_bdlc_code(q, n, d):
    dim = bdlc_file_cache.get(f"Dim_BDLC_{q}_{n}_{d}")
    return LinearCodeRecord(q, n, dim, d)

# #@fork(timeout=3600 * 3)
# def get_min_distance_guava(C, algorithm=None):
#     return C.minimum_distance(algorithm=algorithm)
    
# def get_min_distance(C):
#     guava_min_distance = get_min_distance_guava(C, "guava")
    
#     if isinstance(guava_min_distance, int):
#         return guava_min_distance
    
#     # guava_min_distance = get_min_distance_guava(C)
    
#     # if guava_min_distance is int:
#     #     return guava_min_distance
        
#     max_try = 5
#     while max_try > 0:
#         magma_min_distance = CyclicCodeMinDistance.get_min_distance(len(C.base_field()), C.length(), C.generator_polynomial())
#         if magma_min_distance >= 0:
#             return magma_min_distance
#         sleep((6-max_try)*100  )
#         max_try = max_try - 1
    
    
#    return C.minimum_distance(algorithm="guava")

def get_cyclic_code(factor, code_len):    
    C = codes.CyclicCode(generator_pol=factor, length=code_len)
          
    code_dim = C.dimension()
    
    if should_skip(q, code_len, factor):
        return None
    
    calculated_cache = get_cached_calculeted_cyclic_code(q, code_len, factor)
    if calculated_cache is not None:
        return calculated_cache, C, None
    
    print(f"Calculating min distance: {q}, [{code_len}, {code_dim}] poly: {factor}")
    code_min_dist = C.minimum_distance(algorithm="guava")
    
    # max_try = 5
    # while max_try > 0:
    #     print(f"Trying: {q}, [{code_len}, {code_dim}] poly: {factor}")
    #     code_min_dist = CyclicCodeMinDistance.get_min_distance(len(C.base_field()), C.length(), C.generator_polynomial())
    #     print(f"Got: {code_min_dist}")
    #     if code_min_dist >= 0:
    #         break
    #     sleep((6-max_try)*100  )
    #     max_try = max_try - 1
    
    # if code_min_dist < 0:
    #     code_min_dist = C.minimum_distance(algorithm="guava")
    
    print(f"Calculated: {q}, [{code_len}, {code_dim}, {code_min_dist}]")
    
    is_zero_code = code_dim == 0 and code_min_dist == code_len
    is_LCD = True #is_LCD_code(C)
    
    if not is_zero_code:
        return CyclicCodeRecord(q, code_len, code_dim, code_min_dist, factor), C, is_LCD
    else:
        return None

def handle_bdlc_seach(cyclicCode:CyclicCodeRecord, bdlc:LinearCodeRecord):
    if cyclicCode.k >= bdlc.k:
        print(f"Found: {cyclicCode}")
        save_cyclic_code(cyclicCode, is_LCD)
    

# Find the actual LCD cyclic code
AllSelfRecipFactors_list = []
completed_tasks = 0
if __name__ == '__main__':
    if not os.path.exists("outputs"):
        os.makedirs("outputs")
        
    AllSelfRecipFactors_list = [prepare_factors(m, q) for m, q in m_q_array]
    #AllSelfRecipFactors_list = Parallel(n_jobs=480)(delayed(prepare_factors)(m, q) for m, q in m_q_array)
                               
    total_tasks = sum([len(AllSelfRecipFactors) for AllSelfRecipFactors, m in AllSelfRecipFactors_list])
    print(f"Total tasks: {total_tasks}")
    
    with ProcessPoolExecutor(max_workers=12) as executor:
        print("\nAll factors prepared\n")
        for AllSelfRecipFactors, m in AllSelfRecipFactors_list:
            # Submit tasks all at once
            cyclic_code_features = [executor.submit(get_cyclic_code, f, m) for f in AllSelfRecipFactors]
            
            # get the completed tasks as they are done
            for cyclic_code_feature in as_completed(cyclic_code_features):

                completed_tasks += 1
                print(f"Completed tasks: {completed_tasks}/{total_tasks}")
                
                result = cyclic_code_feature.result()
                                
                if result is None:
                    continue
                cyclicCode, Code, is_LCD  = result
                
                save_cyclic_calculated_code(cyclicCode)
                # if we already cached it use the result
                if is_bdlc_cache_exist(cyclicCode.q, cyclicCode.n, cyclicCode.d):
                    cached_bdlc = get_cached_bdlc_code(cyclicCode.q, cyclicCode.n, cyclicCode.d)
                    handle_bdlc_seach(cyclicCode, cached_bdlc)
                    continue
                else:
                    bdlc_provider.put_request(cyclicCode)
                    print(f"Requesting: {cyclicCode}")
                    if bdlc_provider.get_request_count() < 100:
                        # wait for request to be ready
                        continue
                
                # invoke the online command
                bdlc_results = bdlc_provider.get_results()
                print(f"Got results: {len(bdlc_results)}")
                for echo_cyclic_code, bdlc in bdlc_results:
                    save_bdlc_code(bdlc)
                    handle_bdlc_seach(echo_cyclic_code, bdlc)
                    
    # handle the remaining            
    bdlc_results = bdlc_provider.get_results()        
    for echo_cyclic_lc, bdlc in bdlc_results:
        save_bdlc_code(bdlc)
        handle_bdlc_seach(echo_cyclic_lc, bdlc)