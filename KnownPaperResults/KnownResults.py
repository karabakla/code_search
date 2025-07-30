from functools import lru_cache
from typing import List

import requests
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

def best_known_linear_code_dimension_bound_www(q:int, n:int, k:int):
    if q not in {2, 3, 4, 5, 7, 8, 9}:
        raise ValueError("q must be one of {2, 3, 4, 5, 7, 8, 9}")

    url = f"https://codetables.de/BKLC/BKLC.php?q={q}&n={n}&k={k}"

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        raise IOError(f"Failed to fetch data: {e}")

    html = response.text

    start = html.find("<TABLE>")
    end = html.find("</TABLE>")
    if start == -1 or end == -1:
        raise IOError("Error parsing data (missing <TABLE> tags)")

    parts = html[start + 7:end].split("<TD>")
    try:
        lower_bound = int(parts[2].split("</TD>")[0])
        upper_bound = int(parts[4].split("</TD>")[0])
    except (IndexError, ValueError):
        raise ValueError("Could not extract bounds from response")

    return lower_bound, upper_bound    

@lru_cache(maxsize=40960)
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
    
    try:
        code_tables_lower, code_tables_upper = best_known_linear_code_dimension_bound_www(q, n, k)
        return code_tables_upper
    except:
        pass
    return None

def get_upper_bound_dimension(q:int, n:int, d:int) -> int | str | List[int] | None:
    candidates = []
    for k in range(1, n + 1):
        dist = get_largest_min_distance(q, n, k)
        if isinstance(dist, int) and dist >= d:
            candidates.append(k)

    return max(candidates, default=None)
    

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
                
                f.flush()
                
            f.write("\n")
            
    
# prepare_nk_csv(2, 60)
# prepare_nd_csv(2, 60)

# prepare_nk_csv(3, 50)
# prepare_nd_csv(3, 50)

# print(get_upper_bound_dimension(3, 50, 27))
# print(get_largest_min_distance(2, 11, 3))
# for n in range(2, 10):
#         for k in range(1, 3):
#             result = get_largest_min_distance(2, n, k)
#             print(f"n={n}, k={k}, d={result}")