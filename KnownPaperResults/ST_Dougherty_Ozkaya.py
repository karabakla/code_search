# Proposition 3.2  S.T. Dougherty, J.-L. Kim, B. Ozkaya, L. Sok and P. Sol´e, The combinatorics of LCD codes: linear programming bound and orthogonal matrices

def ST_Dougherty_Ozkaya_Get_Largest_d(q:int, n:int, k:int):
    if q != 2 or n < 2 or k < 1 or k > n:
        return None
    
    n_is_odd = n % 2 != 0
    
    # if k == 1:
    #     return (n - 1) - (n % 2)
    # if k == n - 1:
    #     return 1 + (n % 2)
    
    if n_is_odd:
        if k == 1:
            return n
        if k == n - 1:
            return 2
    else:
        if k == 1:
            return n - 1
        if k == n - 1:
            return 1
        
    return None