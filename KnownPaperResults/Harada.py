# Purpose of this code is to generate know code results.
# Since Harada et. al. papers usually gives algortimic results, we can use this code to generate the results.

from calendar import c


class Harada_nk:
    def __init__(self, q:int, n:int, k:int, result:str):
        self.q = q
        self.n = n
        self.k = k
        self.result = result
        
    def __str__(self):
        return f"Harada_1_nk_q{self.q}({self.n}, {self.k}, {self.result})"
    
    def __repr__(self):
        return self.__str__()
    
    def __dict__(self):
        return {"q":self.q, "n": self.n, "k": self.k, "result": self.result}
    
    def is_exact(self):
        return ',' not in self.result

def Harada_1_Largest_d_q2(n:int, k:int):
    # 6 if (n, k) = (32, 19), (32, 20), (33, 22), (34, 21), (34, 22) and (36, 23),
    if n == 32 and k == 19:
        return 6
    if n == 32 and k == 20:
        return 6
    if n == 33 and k == 22:
        return 6
    if n == 34 and k == 21:
        return 6
    if n == 34 and k == 22:
        return 6
    if n == 36 and k == 23:
        return 6
    
    # 8 if (n, k) = (28, 13), (29, 13) and (30, 14),
    if n == 28 and k == 13:
        return 8
    if n == 29 and k == 13:
        return 8
    if n == 30 and k == 14:
        return 8
    
    # 12 if (n, k) = (28, 6), (30, 7) and (34, 10),
    if n == 28 and k == 6:
        return 12
    if n == 30 and k == 7:
        return 12
    if n == 34 and k == 10:
        return 12
    
    # 16 if (n, k) = (36, 6) and (40, 8),
    if n == 36 and k == 6:
        return 16
    if n == 40 and k == 8:
        return 16
    
    # 18 if (n, k) = (40, 6),
    if n == 40 and k == 6:
        return 18
    
    return None

# Harada 1 section 6 New ternary LCD codes first sentence A classification of ternary LCD codes was done in [1] for n ∈ {1, 2,..., 10}
def Harada_1_Is_Classified_q3(n:int):
    return n in range(1, 11)

"""
# Table 7   
n\\k 4 5 6 7 8 9 10 11 12 13 14 15
11   6 5 4
12   6 5 5 4
13   7 6 6 5 4
14   8 7 6 6 5 4
15   8 8 7 6 5 4 4
16   9 8 7 6 6 5 4 4
17   10 9 8 7 6 6 5 4 4
18   10 9 9 8 7 6 6 5 4 4
19   11 10 9 8 8 7 6 6 5 4 4
20   12 11 10 8,9 8 7,8 7 6 5,6 5 4 3,4
"""

harada_2_known_results_q3_nk = [
    #                4                       5                       6                             7                        8                        9                        10                       11                        12                        13                         14                            15      
    [Harada_nk(3, 11, 4, '6'),  Harada_nk(3, 11, 5, '5'),  Harada_nk(3, 11, 6, '4')],
    [Harada_nk(3, 12, 4, '6'),  Harada_nk(3, 12, 5, '5'),  Harada_nk(3, 12, 6, '5'),  Harada_nk(3, 12, 7, '4')],                                                             
    [Harada_nk(3, 13, 4, '7'),  Harada_nk(3, 13, 5, '6'),  Harada_nk(3, 13, 6, '6'),  Harada_nk(3, 13, 7, '5'), Harada_nk(3, 13, 8, '4')],
    [Harada_nk(3, 14, 4, '8'),  Harada_nk(3, 14, 5, '7'),  Harada_nk(3, 14, 6, '6'),  Harada_nk(3, 14, 7, '6'), Harada_nk(3, 14, 8, '5'), Harada_nk(3, 14, 9, '4')],
    [Harada_nk(3, 15, 4, '8'),  Harada_nk(3, 15, 5, '8'),  Harada_nk(3, 15, 6, '7'),  Harada_nk(3, 15, 7, '6'), Harada_nk(3, 15, 8, '5'), Harada_nk(3, 15, 9, '4'), Harada_nk(3, 15, 10, '4')],
    [Harada_nk(3, 16, 4, '9'),  Harada_nk(3, 16, 5, '8'),  Harada_nk(3, 16, 6, '7'),  Harada_nk(3, 16, 7, '6'), Harada_nk(3, 16, 8, '6'), Harada_nk(3, 16, 9, '5'), Harada_nk(3, 16, 10, '4'), Harada_nk(3, 16, 11, '4')],
    [Harada_nk(3, 17, 4, '10'), Harada_nk(3, 17, 5, '9'),  Harada_nk(3, 17, 6, '8'),  Harada_nk(3, 17, 7, '7'), Harada_nk(3, 17, 8, '6'), Harada_nk(3, 17, 9, '6'), Harada_nk(3, 17, 10, '5'), Harada_nk(3, 17, 11, '4'), Harada_nk(3, 17, 12, '4')],
    [Harada_nk(3, 18, 4, '10'), Harada_nk(3, 18, 5, '9'),  Harada_nk(3, 18, 6, '9'),  Harada_nk(3, 18, 7, '8'), Harada_nk(3, 18, 8, '7'), Harada_nk(3, 18, 9, '6'), Harada_nk(3, 18, 10, '6'), Harada_nk(3, 18, 11, '5'), Harada_nk(3, 18, 12, '4'), Harada_nk(3, 18, 13, '4')],
    [Harada_nk(3, 19, 4, '11'), Harada_nk(3, 19, 5, '10'), Harada_nk(3, 19, 6, '9'),  Harada_nk(3, 19, 7, '8'), Harada_nk(3, 19, 8, '8'), Harada_nk(3, 19, 9, '7'), Harada_nk(3, 19, 10, '6'), Harada_nk(3, 19, 11, '6'), Harada_nk(3, 19, 12, '5'), Harada_nk(3, 19, 13, '4'), Harada_nk(3, 19, 14, '4')],
    [Harada_nk(3, 20, 4, '12'), Harada_nk(3, 20, 5, '11'), Harada_nk(3, 20, 6, '10'), Harada_nk(3, 20, 7, '8,9'), Harada_nk(3, 20, 8, '8'), Harada_nk(3, 20, 9, '7,8'), Harada_nk(3, 20, 10, 7), Harada_nk(3, 20, 11, '6'), Harada_nk(3, 20, 12, '5,6'), Harada_nk(3, 20, 13, '5'), Harada_nk(3, 20, 14, '4'), Harada_nk(3, 20, 15, '3,4')],
    [Harada_nk(3, 34, 22, '7,8')],
    [Harada_nk(3, 37, 23, '7,9'), Harada_nk(3, 37, 29, '5')],
    [Harada_nk(3, 40, 30, '5,6')]
]

def Harada_2_Largest_d_q3(n:int, k:int):
    # From Proposition 7.4  - 7.6
    if n >= 3 and k == n - 2:
        return 2
    
    if n >= 4 and k == n - 3:
        if n == 4:
           return 4
        if n <= 10:
           return 3 
        else: 
            return 2
    if n >= 5 and k == n - 4:
        if n == 5:
            return 5
        if n <= 8:
            return 4
        if n <= 36:
            return 3
        else:
            2
    
    try:
    # From Table 7
        #return max(nk.result for row_nk in harada_2_known_results_q3_nk for nk in row_nk if nk.n == n and nk.k == k and nk.is_exact())
        return max(nk.result for row_nk in harada_2_known_results_q3_nk for nk in row_nk if nk.n == n and nk.k == k)
    except:
        return None

def Harada_2_Largest_d_q2(n:int, k:int):
    if n>= 5 and k == n - 5:
        if n == 6:
            return 5
        if n in [7, 9, 11]:
            return 4
        if n in range(8, 27):
            return 3
        else:
            return 2

# Harada_7_2018_On the minimum weights of binary LCD codes Theorem 1 & 2 
# Harada 3 Section 6.2.1 Determination of d2(n, 4) and Proposition 6.5
def Harada_3_Largest_d_q2_k4(n:int):
    # if n ≡ 5, 9, 13 (mod 15), -> floor(8n/15)
    # if n ≡ 1, 2, 3, 4, 6, 7, 8, 10, 11, 12, 14 (mod 15) -> floor(8n/15) - 1
    # if n ≡ 0 (mod 15) -> floor(8n/15) - 2
            
    mod15_result = n % 15
    floor_8n_15 = n * 8 // 15 # integer division in python equals to floor
    
    if mod15_result in [5, 9, 13]:
        return floor_8n_15
    
    if mod15_result in [1, 2, 3, 4, 6, 7, 8, 10, 11, 12, 14]:
        return floor_8n_15 - 1
    
    if mod15_result == 0:
        return floor_8n_15 - 2
    
    return None

def Harada_3_Largest_d_q3(n:int, k:int):
    # Harada 3 Section 7.1.1 Determination of d3(n, 2)
    if k == 2:
        mod_result = n % 4
        floor_result = 3*n // 4
        if mod_result == 1 or mod_result == 2:
            return floor_result
        return floor_result - 1
    
    # Harada 3 Section 7.2.1 Determination of d3(n, 3)
    if k == 3:
        mod_result = n % 13
        floor_result = 9*n // 13
        if mod_result == 4 or mod_result == 7 or mod_result == 10:
            return floor_result
        return floor_result - 1

#q_2(n, n − 5) = 5 if n = 6, 4 if n in {7, 9, 11}, 3 if n in {8, 10, 12, 13 ...,26} and 2 if n ≥ 27,
#q_2(n, n − 6) = 7 if n = 7, 5 if n = 8, 4 if n in {9, 10, . . . , 16, 18, 20, 22, 24, 26}, 3 if n in {17, 19, 21, 23, 25, 27, 28, . . . , 57} and 2 if n ≥ 58,
#q_2(n, n − 7) = 7 if n = 8, 6 if n = 9, 5 if n = 10, 4 if n in {11, 12, . . . , 31, 33, 35, ..., 57 }, 3 if n in {65, 66, . . . , 120} and 2 is n >= 121

#q_3(n, n - 4) = 5 if n = 5, 4 if n in {6, 7, 8}, 3 if n in {9,...36} and 2 if n ≥ 37
#q_3(n, n − 5) = 5 if n = 6, 4 if n in {7, 8, . . . , 19}, 3 if n in {20, 21, . . . , 116} and 2 if n >= 117
#q_3(n, n − 6) = 7 if n = 7, 5 if n in {8, 9, . . . , 14}, 4 if n in {15, 16, . . . , 50}, 3 or 4 if n in {51, 52, . . . , 56}, 3 if n in {57, 58, . . . , 358}, 2 if n ∈ {359, 360, . . .}

# Remark 5.4. Our non-exhaustive computer search failed to discover a binary
# LCD [n, n−7, 4] code for n = 34, 36, 38, 40, 42, 44, 46, 48, 50, 52, 54, 56, 58, 59, . . . , 63 and 64. For these n, a classification of binary [n, n − 7, 4] codes is beyond our current computer resources.

def Harada_4_Get_Largest_Known_d(q:int, n:int, k:int) -> int:
    if q == 2:
        if k == n - 5:
            if n == 6:
                return 5
            if n in [7, 9, 11]:
                return 4
            if n in range(8, 27):
                return 3
            if n >= 27:
                return 2    
        if k == n - 6:
            if n == 7:
                return 7
            if n == 8:
                return 5
            if n in range(9, 17) or  n in [18, 20, 22, 24, 26]:
                return 4
            if n in [17, 19, 21, 23, 25, 27, 28] or n in range(29, 58):
                return 3
            else:
                return 2
        if k == n - 7:
            if n == 8:
                return 7
            if n == 9:
                return 6
            if n == 10:
                return 5
            if n in range(11, 32) or n in [33, 35, 37, 39, 41, 43, 45, 47, 49, 51, 53, 55, 57]:
                return 4
            if n in range(65, 121):
                return 3
            if n in [34, 36, 38, 40, 42, 44, 46, 48] or n in [50, 52, 54, 56, 58, 59] or n in range(60, 65):
                return [3, 4]
            if n >= 121:
                return 2
            
    if q == 3:
        if k == n - 4:
            if n == 5:
                return 5
            if n in [6, 7, 8]:
                return 4
            if n in range(9, 37):
                return 3
            if n >= 37:
                return 2
        if k == n - 5:
            if n == 6:
                return 5
            if n in range(7, 20):
                return 4
            if n in range(20, 117):
                return 3
            else:
                return 2
        
        if k == n - 6:
            if n == 7:
                return 7
            if n in range(8, 15):
                return 5
            if n in range(15, 51):
                return 4
            if n in range(57, 358):
                return 3
            if n in range(51, 57):
                return [3, 4]
            if n >= 359:
                return 2
                
    return None

def Harada_4_Is_Largest_d_Known(q:int, n:int, k:int) -> bool:
    if q < 2 or n < 1 or k < 0 or k > n:
        raise ValueError("q, n, k apporopriate values")
    
    if Harada_4_Get_Largest_Known_d(q, n, k) is not None:
        return True
     
    if q == 2:
        return k <= 5 or k >= n - 6
    if q == 3:
        return k <= 3 or k >= n - 5

# https://arxiv.org/pdf/1802.06985 Table 3
# harada_2018_known_results_q2_raw = """
# n\k  2       3          4           5           6           7           8           9           10          11          12          13          14          15
# 2   
# 3   (2, 1)
# 4   (2, 2)  (1, 2)
# 5   (2, 3)  (2, 1)      (2, 1)
# 6   (3, 2)  (2, 3)      (2, 4)      (1, 3)
# 7   (4, 1)  (3, 1)      (2, 9)      (2, 2)      (2, 1)
# 8   (5, 1)  (3, 3)      (3, 1)      (2, 9)      (2, 6)      (1, 4)
# 9   (6, 1)  (4, 1)      (4, 1)      (3, 2)      (2, 23)     (2, 3)      (2, 1)
# 10  (6, 2)  (5, 1)      (4, 5)      (3, 11)     (3, 2)      (2, 23)     (2, 9)      (1, 5)
# 11  (6, 4)  (5, 6)      (4, 20)     (4, 4)      (4, 1)      (3, 1)      (2, 51)     (2, 4)      (2, 1)  
# 12  (7, 2)  (6, 1)      (5, 6)      (4, 37)     (4, 11)     (3, 22)     (2, 396)    (2, 51)     (2, 12)     (1, 6)
# 13  (8, 1)  (6, 6)      (6, 2)      (5, 5)      (4, 146)    (4, 4)      (3, 27)     (2, 619)    (2, 103)    (2, 5)      (2, 1)
# 14  (9, 1)  (7, 1)      (6, 16)     (5, 101)    (5, 4)      (4, 301)    (4, 8)      (3, 31)     (2, 1370)   (2, 103)    (2, 16)     (1, 7)  
# 15  (10, 1) (7, 8)      (6, 89)     (6, 10)     (6, 2)      (5, 1)      (4, 985)    (4, 2)      (3, 34)     (2, 2143)   (2, 196)    (2, 7)      (2, 1)
# 16  (10, 2) (8, 1)      (7, 7)      (6, 283)    (6, 60)     (5, 1596)   (5, 1)      (4, 1772)   (4, 7)      (3, 34)     (2, 4389)   (2, 196)    (2, 20)     (1, 8)
# """

# for n, line in enumerate(harada_2018_known_results_q2_raw.split("\n")):
#     if n < 3:
#         continue
    
#     row = []
#     for k_raw, result_raw in enumerate(line.split('(')):
#         if k_raw < 1:
#             continue
#         k = k_raw + 1
#         result = result_raw.split(',')[0]
#         row.append(f"Harada_nk(2, {n}, {k}, '{result}')")
        
#     print(f"[{', '.join(row)}],")

harada_2018_known_results_q2_nk = [
    [Harada_nk(2, 3, 2, '2')],
    [Harada_nk(2, 4, 2, '2'), Harada_nk(2, 4, 3, '1')],
    [Harada_nk(2, 5, 2, '2'), Harada_nk(2, 5, 3, '2'), Harada_nk(2, 5, 4, '2')],
    [Harada_nk(2, 6, 2, '3'), Harada_nk(2, 6, 3, '2'), Harada_nk(2, 6, 4, '2'), Harada_nk(2, 6, 5, '1')],
    [Harada_nk(2, 7, 2, '4'), Harada_nk(2, 7, 3, '3'), Harada_nk(2, 7, 4, '2'), Harada_nk(2, 7, 5, '2'), Harada_nk(2, 7, 6, '2')],
    [Harada_nk(2, 8, 2, '5'), Harada_nk(2, 8, 3, '3'), Harada_nk(2, 8, 4, '3'), Harada_nk(2, 8, 5, '2'), Harada_nk(2, 8, 6, '2'), Harada_nk(2, 8, 7, '1')],
    [Harada_nk(2, 9, 2, '6'), Harada_nk(2, 9, 3, '4'), Harada_nk(2, 9, 4, '4'), Harada_nk(2, 9, 5, '3'), Harada_nk(2, 9, 6, '2'), Harada_nk(2, 9, 7, '2'), Harada_nk(2, 9, 8, '2')],
    [Harada_nk(2, 10, 2, '6'), Harada_nk(2, 10, 3, '5'), Harada_nk(2, 10, 4, '4'), Harada_nk(2, 10, 5, '3'), Harada_nk(2, 10, 6, '3'), Harada_nk(2, 10, 7, '2'), Harada_nk(2, 10, 8, '2'), Harada_nk(2, 10, 9, '1')],
    [Harada_nk(2, 11, 2, '6'), Harada_nk(2, 11, 3, '5'), Harada_nk(2, 11, 4, '4'), Harada_nk(2, 11, 5, '4'), Harada_nk(2, 11, 6, '4'), Harada_nk(2, 11, 7, '3'), Harada_nk(2, 11, 8, '2'), Harada_nk(2, 11, 9, '2'), Harada_nk(2, 11, 10, '2')],
    [Harada_nk(2, 12, 2, '7'), Harada_nk(2, 12, 3, '6'), Harada_nk(2, 12, 4, '5'), Harada_nk(2, 12, 5, '4'), Harada_nk(2, 12, 6, '4'), Harada_nk(2, 12, 7, '3'), Harada_nk(2, 12, 8, '2'), Harada_nk(2, 12, 9, '2'), Harada_nk(2, 12, 10, '2'), Harada_nk(2, 12, 11, '1')],
    [Harada_nk(2, 13, 2, '8'), Harada_nk(2, 13, 3, '6'), Harada_nk(2, 13, 4, '6'), Harada_nk(2, 13, 5, '5'), Harada_nk(2, 13, 6, '4'), Harada_nk(2, 13, 7, '4'), Harada_nk(2, 13, 8, '3'), Harada_nk(2, 13, 9, '2'), Harada_nk(2, 13, 10, '2'), Harada_nk(2, 13, 11, '2'), Harada_nk(2, 13, 12, '2')],
    [Harada_nk(2, 14, 2, '9'), Harada_nk(2, 14, 3, '7'), Harada_nk(2, 14, 4, '6'), Harada_nk(2, 14, 5, '5'), Harada_nk(2, 14, 6, '5'), Harada_nk(2, 14, 7, '4'), Harada_nk(2, 14, 8, '4'), Harada_nk(2, 14, 9, '3'), Harada_nk(2, 14, 10, '2'), Harada_nk(2, 14, 11, '2'), Harada_nk(2, 14, 12, '2'), Harada_nk(2, 14, 13, '1')],
    [Harada_nk(2, 15, 2, '10'), Harada_nk(2, 15, 3, '7'), Harada_nk(2, 15, 4, '6'), Harada_nk(2, 15, 5, '6'), Harada_nk(2, 15, 6, '6'), Harada_nk(2, 15, 7, '5'), Harada_nk(2, 15, 8, '4'), Harada_nk(2, 15, 9, '4'), Harada_nk(2, 15, 10, '3'), Harada_nk(2, 15, 11, '2'), Harada_nk(2, 15, 12, '2'), Harada_nk(2, 15, 13, '2'), Harada_nk(2, 15, 14, '2')],
    [Harada_nk(2, 16, 2, '10'), Harada_nk(2, 16, 3, '8'), Harada_nk(2, 16, 4, '7'), Harada_nk(2, 16, 5, '6'), Harada_nk(2, 16, 6, '6'), Harada_nk(2, 16, 7, '5'), Harada_nk(2, 16, 8, '5'), Harada_nk(2, 16, 9, '4'), Harada_nk(2, 16, 10, '4'), Harada_nk(2, 16, 11, '3'), Harada_nk(2, 16, 12, '2'), Harada_nk(2, 16, 13, '2'), Harada_nk(2, 16, 14, '2'), Harada_nk(2, 16, 15, '1')]
]

# Binary linear complementary dual codes, Harada et. al. 2018
# Section 4, floor(2n/3) if n ≡ 1, 2, 3, 4 (mod 6) otherwise floor(2n/3) − 1
# Theorem 5.1 floor(4n/7) if n ≡ 3, 5 (mod 7), otherwise floor(4n/7) − 1
def Harada_2018_Get_Largest_Known_d_q2(n:int, k:int) -> int:
    # Also shown here  L. Galvez, J.-L. Kim, N. Lee, Y.G. Roe and B.-S. Won, Some bounds on binary LCD codes
    if k == 2:
        floor_result = (n * 2) // 3
        if n % 6 in [1, 2, 3, 4]:
            return floor_result
        return floor_result - 1
    if k == 3:
        floor_result = n * 4 // 7
        if n % 7 in [3, 5]:
            return floor_result
        return floor_result - 1
    
    
    #Lucky Galvez et al. Some Bounds on Binary LCD Codes Proposition 3.2.
    # Given i ≥ 2, LCD[n, n − i] = 2 for all n ≥ 2^i
    # k = n - i -> i = n - k
    # n >= 2^i -> n >= 2^(n - k)
    # i>=2 -> n - k >= 2 -> n >= k + 2
    # 
    # d(n, n − 2) = 2 for n ≥ 4
    # d(n, n − 3) = 2 for n ≥ 8 
    # d(n, n − 4) = 2 for n ≥ 16
    if n >= k + 2 and n >= 2 ** (n - k):
        return 2
    
    try:
        return max(nk.result for row_nk in harada_2018_known_results_q2_nk for nk in row_nk if nk.n == n and nk.k == k and nk.is_exact())
    except:
        return None
    

#Harada_2018(https://arxiv.org/pdf/1803.11335) Proposition 5. Let Cn,k denote the set of all inequivalent ternary LCD [n, k]
def Harada_2018_Get_Largest_Known_d_q3(n:int, k:int) -> int:
    if k == 1:
        if n % 3 == 0:
            return n - 1  # Largest d < n and not divisible by 3
        else:
            return n # Largest d < n and not divisible by 3
    elif k == n - 1:
        if n % 3 == 0:
            return 1  # Largest d is 1 when n ≡ 0 (mod 3)
        else:
            return 2
    
    return None

def Harada_Get_Largest_d(q:int, n:int, k:int) -> int:
    if q == 2:
        if Harada_2018_Get_Largest_Known_d_q2(n, k) is not None:
            return Harada_2018_Get_Largest_Known_d_q2(n, k)
                
        if k == 4:
            if Harada_3_Largest_d_q2_k4(n) is not None:
                return Harada_3_Largest_d_q2_k4(n)
        
        if Harada_1_Largest_d_q2(n, k) is not None:
            return Harada_1_Largest_d_q2(n, k)
    
    if Harada_4_Get_Largest_Known_d(q, n, k) is not None:
        return Harada_4_Get_Largest_Known_d(q, n, k)
    
    if q == 3:
        if Harada_2018_Get_Largest_Known_d_q3(n, k) is not None:
            return Harada_2018_Get_Largest_Known_d_q3(n, k)
        if Harada_3_Largest_d_q3(n, k) is not None:
            return Harada_3_Largest_d_q3(n, k)
        
        return Harada_2_Largest_d_q3(n, k)
                
    return None