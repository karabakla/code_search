from typing import List
from KnownPaperResults.BinBinPang import BinBinPang_Get_Largest_Known_d
from KnownPaperResults.Harada import Harada_Get_Largest_d
from KnownPaperResults.ST_Dougherty_Ozkaya import ST_Dougherty_Ozkaya_Get_Largest_d
from KnownPaperResults.Stefka import Stefka_Get_Largest_d
from KnownPaperResults.YangLiu import YangLiu_Get_Largest_d
from KnownPaperResults.Wang import Wang_Get_Largest_d

def simple_known_results(n:int, k:int):
    # Zero code
    if n == k:
        return 1
    
    return None
    

def get_largest_min_distance(q:int, n:int, k:int) -> int | str | List[int] | None:
    
    simple_known_results_result = simple_known_results(n, k)
    if simple_known_results_result is not None:
        return simple_known_results_result
    
    st_dougherty_ozkaya_result = ST_Dougherty_Ozkaya_Get_Largest_d(q, n, k)
    if st_dougherty_ozkaya_result is not None:
        return st_dougherty_ozkaya_result
    
    bin_bin_pang_result = BinBinPang_Get_Largest_Known_d(q, n, k)
    if bin_bin_pang_result is not None:
        return bin_bin_pang_result
    
    yang_liu_result = YangLiu_Get_Largest_d(q, n, k)
    if yang_liu_result is not None:
        return yang_liu_result
    
    stefka_result = Stefka_Get_Largest_d(q, n, k)
    
    if stefka_result is not None:
        return stefka_result
    
    wang_result = Wang_Get_Largest_d(q, n, k)
    if wang_result is not None:
        return wang_result
    
    harada_result = Harada_Get_Largest_d(q, n, k)
    
    if harada_result is not None:
        return harada_result
    
    return None

def get_upper_bound_dimension(q:int, n:int, d:int) -> int | str | List[int] | None:
    return max([k for k in range(1, n+1) if get_largest_min_distance(q, n, k) == d], default=None)
    

# for d in range(1, 33):
#     result = get_upper_bound_dimension(2, 33, d)
#     print(f"n={33}, d={d}, k={result}")


def prepare_nk_csv(q:int, n_max:int):
    with open(f"CombinedResults_nk_{q}_nmax_{n_max}.csv", "w") as f:
        for n in range(q, n_max+1):
            for k in range(1, n+1):
                result = get_largest_min_distance(q, n, k)
                if result is not None:
                    f.write(f"{result},")
                else:
                    f.write(f"_,")
                
            f.write("\n")
            
def prepare_nd_csv(q:int, n_max:int):    
   with open(f"CombinedResults_nd_{q}_nmax_{n_max}.csv", "w") as f:
        for n in range(2, n_max+1):
            for d in range(1, n+1):
                result = max([k for k in range(1, n+1) if get_largest_min_distance(q, n, k) == d], default=None)
                if result is not None:
                    f.write(f"{result},")
                else:
                    f.write(f"_,")
                
            f.write("\n")
            
    
# prepare_nk_csv(2, 60)
# prepare_nd_csv(2, 60)

# prepare_nk_csv(3, 50)
# prepare_nd_csv(3, 50)

# print(get_largest_min_distance(2, 60, 53))
# print(get_largest_min_distance(2, 11, 3))
# for n in range(2, 10):
#         for k in range(1, 3):
#             result = get_largest_min_distance(2, n, k)
#             print(f"n={n}, k={k}, d={result}")