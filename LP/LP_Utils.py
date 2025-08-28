import math
from sage.all import binomial, Integer, codes # type: ignore
from sage.coding.code_bounds import dimension_upper_bound,elias_upper_bound, hamming_upper_bound, plotkin_upper_bound,singleton_upper_bound # type: ignore

def krawtchouk(n:int, q:int, j:int, x:int) -> int:
    return int(sum([(-1)**k *(q-1)**(j-k) * binomial(x,k) * binomial(n-x, j-k) for k in range(j+1)]))

def volume_of_hamming_ball(n:int, r:int, q:int) -> int:
    return sum((q-1)**i * binomial(n, i) for i in range(r+1))

def gilbert_bound_k(q:int, n:int, d:int) -> int:
    return int(math.log(q**n / volume_of_hamming_ball(n, d-1, q), q))

def gilbert_varshamov_linear_bound_k(q:int, n:int, d:int) -> int:
    if d < 2:
        return 0
    
    if d == 2:
        if n % 2 == 0:
            return n-2
        else:
            return n-1
    
    # ------------------------------------------------------
    # gilbert_varshamov bound for linear codes
    vol = Integer(1 + volume_of_hamming_ball(n-1, d-2, q))
    
    if vol.is_power_of(q):
        k_gilbert_varshamov = int(n - vol.exact_log(q))
    else:
        k_gilbert_varshamov = int(n - math.ceil(vol.log(q)))
    # -------------------------------------------------------
    
    k_mds = n - d + 1
    if q == 2 and k_gilbert_varshamov >= k_mds:
        return gilbert_bound_k(q, n, d) # there is no mds code in q=2

    return k_gilbert_varshamov

def gilbert_varshamov_bound_find_lower_dual_distance(q:int, n:int, k:int) -> int:
    j = 0
    bound = binomial(n, j)* (q-1)**j
    while bound < q**k:
        j += 1
        bound += binomial(n, j)* (q-1)**j
        
    return j+ 1

def code_minimum_distance_upper_bound(q:int, n:int, k:int) -> int:
    for d in range(2, n+1):
        try:
            k_lo = dimension_upper_bound(n, d, q) #gilbert_varshamov_linear_bound_k(q, n, d) # type: ignore
            if k_lo <= k:
                return d            
        except:
            pass

    return -1

def safe_bound_call(func, *args):
    try:
        return func(*args)
    except:
        return -1
    
def safe_dimension_upper_bound(n, d, q) -> int:   # type:ignore
    eub = safe_bound_call(elias_upper_bound, n, q, d) # type:ignore
    hub = safe_bound_call(hamming_upper_bound, n, q, d)  # type:ignore
    pub = safe_bound_call(plotkin_upper_bound, n, q, d)  # type:ignore
    sub = safe_bound_call(singleton_upper_bound, n, q, d)  # type:ignore

    return int(math.log(max(eub, hub, pub, sub), q))  # type:ignore

# print(code_minimum_distance_upper_bound(2, 25, 15))

# n = 7
# q = 2
# i = 4
# j = 3
# k = krawtchouk(n, q, j, i)
# symetric_k = krawtchouk(n, q, i, j) * (q-1)**j*binomial(n, j)/((q-1)**i*binomial(n, i))
# print(krawtchouk(n, q, i, j))