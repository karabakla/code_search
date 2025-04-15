# https://arxiv.org/pdf/1804.00799
# Some new bounds on LCD codes over finite fields
# Section 5 The exact value of LD(n, 2) over F3

# Theorem 5.2. LD(n, 2) ≤ floor(3n/4) for n ≥ 2

# Theorem 5.3. Let n ≥ 2. Then LD(n, 2) = floor(3n/4) for n ≡ 1, 2 (mod 4).

# Theorem 5.4. Let n ≥ 2. Then LD(n, 2) = floor(3n/4) − 1 for n ≡ 0, 3 (mod 4)

def BinBinPang_Get_Largest_Known_d_k2_q3(n:int):
    mod_result = n % 4
    floor_result = (3*n) // 4
    
    if mod_result == 1 or mod_result == 2:
        return floor_result
    if mod_result == 0 or mod_result == 3:
        return floor_result - 1
    
def BinBinPang_Get_Largest_Known_d(q:int, n:int, k:int):
    if q != 3 or k != 2:
        return None
    
    return BinBinPang_Get_Largest_Known_d_k2_q3(n)