from collections import deque
from typing import Tuple, Set
from LCDCodePool.GetClosestLCD import get_bdlc_codes
from Utils.Code_Utils import is_zero_code, safe_minimum_distance
from Utils.MagmaUtils import MagmaSession
from sage.all import * # type: ignore
from sage.coding.linear_code import LinearCode # type: ignore
from sage.coding.code_constructions import *   # type: ignore
from sage.coding.punctured_code import _puncture # type: ignore
from math import sqrt

# def create_magma_session(thread_count = 1):
#     magma_session = MagmaSession(f"{os.getcwd()}/Utils/Magma/MagmaCodes", thread_count)
#     magma_session.magma.set_seed(0)
#     return magma_session

# magma_session = create_magma_session(4)

def is_lcd_code(C:LinearCode) -> bool:
    """
    Returns True if C is a Linear Complementary Dual (LCD) code, False otherwise.
    """
    G = C.generator_matrix()
    return not ((G * G.transpose()).is_singular())

# def punctured_code(C:LinearCode, punctured_indices:set[int]) -> LinearCode:
#     """
#     Returns the punctured code of C with the punctured indices
#     """
#     return codes.PuncturedCode(C, punctured_indices) # type: ignore

# def shortened_code(C:LinearCode, shortened_indices:set[int]) -> LinearCode:
#     """
#     Returns the shortened code of C with the shortened indices
#     """
    
#     generator_matrix = C.generator_matrix()
    
#     new_generator_matrix = []
#     for row in generator_matrix:
#         if all([row[index] == 0 for index in shortened_indices]):
#             new_row = _puncture(row, shortened_indices)
#             new_generator_matrix.append(new_row)
            
#     if len(new_generator_matrix) == 0:
#         # zero code
#         return LinearCode(matrix(C.base_ring(), 0, C.length())) # type: ignore
    
#     return LinearCode(matrix(C.base_ring(), new_generator_matrix)) # type: ignore

# def shortened_code(C, zero_coords) -> LinearCode:
#     # add 1 to each index to match magma's 1-based indexing
#     for _ in range(100):
#         try:
#             new_code_generator_matrix = magma_session.magma.ShortenCode(C, set([i+1 for i in zero_coords])).GeneratorMatrix().sage()
#             return LinearCode(new_code_generator_matrix)
#         except:
#             pass
#     raise Exception("Could not generate shortened code")
    # r"""
    # Shorten the linear code C by forcing the coordinates in `zero_coords`
    # to be zero, then removing those coordinates from the code.

    # INPUT:
    # - `C`          -- a linear code (sage.coding.linear_code.LinearCode)
    # - `zero_coords` -- a list (or set) of coordinates to be forced to zero

    # OUTPUT:
    # - A new LinearCode instance, the shortened code of C on `zero_coords`.

    # EXAMPLE:
    #     # Suppose C is an [n,k] linear code over GF(q).
    #     # We want to shorten on coordinates [0,1] (forcing them to be zero).
    #     shortened_C = shorten_linear_code(C, [0,1])

    # ALGORITHM:
    #     1. Extract the generator matrix G of C, of size k x n.
    #     2. Reorder columns of G so that the `zero_coords` are placed last.
    #        Let keep_coords be the complement (the coordinates you keep).
    #     3. Partition G into [ G_keep | G_zero ]:
    #         - G_keep corresponds to columns you will keep.
    #         - G_zero corresponds to columns forced to zero.
    #     4. Solve x * G_zero = 0 for x in the right kernel of G_zero^T.
    #     5. For each basis vector x of that kernel, x * G_keep is a row
    #        in the generator matrix of the shortened code.
    #     6. Construct and return the new linear code spanned by these row vectors.
    # """    
    # # Basic checks
    # n = C.length()
    # if max(zero_coords) >= n or min(zero_coords) < 0:
    #     raise ValueError("Some coordinates to shorten on are out of range.")
    
    # # Convert zero_coords to a sorted list (if not already)
    # zero_coords = sorted(zero_coords)
    # # Coordinates that we keep:
    # keep_coords = [i for i in range(n) if i not in zero_coords]
    
    # # Get generator matrix of C
    # G = C.generator_matrix()  # size: k x n
    
    # # Reorder columns so that "keep_coords" come first, then "zero_coords"
    # new_order = keep_coords + zero_coords
    # G_reordered = G[:, new_order]
    
    # # Split into G_keep and G_zero
    # #   G_keep has the columns we keep
    # #   G_zero has the columns forced to zero
    # k = G.nrows()
    # len_keep = len(keep_coords)
    # G_keep = G_reordered[:, :len_keep]      # size: k x len_keep
    # G_zero = G_reordered[:,  len_keep: ]    # size: k x (len(zero_coords))
    
    # # We want all vectors x of length k (over GF(q)) satisfying x * G_zero = 0.
    # #   That is the same as G_zero^T * x^T = 0  --> x is in the right kernel of G_zero^T.
    # M = G_zero.transpose()
    # sol_space = M.right_kernel()  # space of dimension = ?

    # # Build a generator matrix for the shortened code by:
    # #   for each solution x in that kernel, take the row x * G_keep
    # basis_solutions = sol_space.basis()
    
    # new_gen_rows = []
    # for x in basis_solutions:
    #     # x is a row vector in GF(q)^k
    #     # The shortened codeword (in length len_keep) is x * G_keep
    #     row = x * G_keep
    #     new_gen_rows.append(row)
    
    # if not new_gen_rows:
    #     # If the only solution is the trivial one, the shortened code is {0}
    #     from sage.matrix.all import zero_matrix
    #     new_G = zero_matrix(G.base_ring(), 0, len_keep)
    # else:
    #     new_G = matrix(new_gen_rows)

    # from sage.coding.linear_code import LinearCode
    # shortened_C = LinearCode(new_G)
    
    # return shortened_C
 
def random_vector_From(field, dimension) -> vector: # type: ignore
    """
    Returns a random vector from the field
    """
    return VectorSpace(field, dimension).random_element() # type: ignore

def random_matrix_From(field, rows, cols) -> matrix: # type: ignore
    """
    Returns a random matrix from the field
    """ 
    return MatrixSpace(field, rows, cols).random_element() # type: ignore

def inner_product(v1:vector, v2:vector) -> int: # type: ignore
    """
    Returns the inner product of two vectors
    """
    return v1.dot_product(v2)

def select_best_possible_sub_dual_matrix(C:LinearCode, rows_count:int, max_iteration:int) -> Matrix: # type: ignore
    """
    Selects a best dual random matrix in terms of minimum weight using bfs
    """ 
    def _get_min_weight(m:Matrix) -> int: # type: ignore
        if (m*m.transpose()).is_singular():
            return -1
        new_code = LinearCode(m.stack(C.generator_matrix()))
        return safe_minimum_distance(new_code)
    
    min_distance = safe_minimum_distance(C)
    
    dual_C = C.dual_code()
    best_sub_matrix = None
    best_min_distance = -1
    for _ in range(max_iteration):
        random_dual_matrix = Matrix(C.base_ring(), [dual_C.random_element() for _ in range(rows_count)]) # type: ignore
        if random_dual_matrix.rank() != rows_count:
            continue
        matrix_min_distance = _get_min_weight(random_dual_matrix)
        if matrix_min_distance == -1:
            continue
        if matrix_min_distance >= min_distance:
            return random_dual_matrix
        if matrix_min_distance > best_min_distance:
            best_min_distance = matrix_min_distance
            best_sub_matrix = random_dual_matrix
    
    return best_sub_matrix
    # random_dual_codes = [[dual_C.random_element() for _ in range(rows_count)] for _ in range(max_iteration)]
    
    # sub_matrices = [matrix(C.base_ring(), random_dual_codes[i]) for i in range(max_iteration)]
    
    # min_weights = [_get_min_weight(Matrix(C.base_ring(), g)) for g in sub_matrices if g.rank() == rows_count]
    # best_sub_matrix = max(sub_matrices, key=lambda g: _get_min_weight(Matrix(C.base_ring(), g)))
    
    # return best_sub_matrix

def lemma_4_1_generate_new_code_from(C:LinearCode, i:int) -> Tuple[LinearCode, str, int]:
    """
    if C is a binary LCD code with d ≥ 2 and d^⊥ ≥ 2 then exactly one of the codes C_i and C^i is also LCD.
    Where C_i is the shortened code and C^i is the punctured code
    """
    if not is_lcd_code(C):
        raise ValueError("C is not an LCD code")
    
    min_distance_d = safe_minimum_distance(C)
    min_distance_d_dual = safe_minimum_distance(C.dual_code())
    if min_distance_d < 2 or min_distance_d_dual < 2:
        return C, f"{lemma_4_1_generate_new_code_from.__name__} skipped since d < 2 or d^⊥ < 2", i
    
    C_s = C.shortened([i])
    if is_lcd_code(C_s):
        return C_s, f"{lemma_4_1_generate_new_code_from.__name__} shortened code at {i}", i
    
    C_p = C.punctured([i])
    if is_lcd_code(C_p):
        return C_p, f"{lemma_4_1_generate_new_code_from.__name__} punctured code at {i}", i
    
    return C, f"{lemma_4_1_generate_new_code_from.__name__} skipped since both shortened and punctured codes are not LCD", i
    #raise ValueError(f"Generated code is not an LCD code for i = {i}, C = {C}")
    
def prop_4_2_generate_new_code_from(C:LinearCode, r:int) -> Tuple[LinearCode, str, Tuple[vector,vector]]: # type: ignore
    """
    m = r-1
    given a linear code C, returns a new linear code C' with [n+r, k] parameters iff p | m(1+m)
    """
    if not is_lcd_code(C):
        raise ValueError("C is not an LCD code")
    
    p = C.base_ring().characteristic()
    m = r-1        
    
    if not p.divides(m*(1+m)):
        raise ValueError("p does not divide r(1+r)")
    
    G = C.generator_matrix()
    field = C.base_ring()
    n = G.ncols()
    k = G.nrows()
    if n <= k:
        return C, f"{prop_4_2_generate_new_code_from.__name__} r = {r} skipped", (None, None)
    
    V = matrix(field, r, k) # type: ignore
        
    v = random_vector_From(field, k)

    for i in range(m):
        V[i] = v
    
    V[-1] = v * (p-m)
    V = V.transpose()
            
    G_new = V.augment(G)
    
    MS = MatrixSpace(field, k, n+r) # type: ignore
    new_code = LinearCode(MS(G_new))
    
    if not is_lcd_code(new_code):
        raise ValueError("Generated code is not an LCD code")
    
    return new_code, f"{prop_4_2_generate_new_code_from.__name__} r = {r}", (v, (p-m)*v)

def theorem_4_3_extended_const_method_generate_new_code_from(C:LinearCode, r:int) -> Tuple[LinearCode,str, Tuple[vector, vector, vector]]: # type: ignore
    """
    given a linear code C, returns a new linear code C' with [n+r, k+1] parameters iff following conditions are satisfied:
    for x in Fq**n, and a and b in Fq^r, were r_i is the ith row of the generator matrix of C:
    1- p not divides (inner_product(a,a) + inner_product(x,x))
    2- p divides inner_product(b,b) 
    3- p divides (inner_product(b,a) + 1)

    such that inner_product(x, r_i) != 0 for all r_i in G
    
    """
    if not is_lcd_code(C):
        raise ValueError("C is not an LCD code")
    
    def condition_1(p:Integer, a:vector, x:vector) -> bool: # type: ignore
        """
        Returns True if p not divides inner_product(a,a) + inner_product(x,x)
        """
        return not p.divides((inner_product(a,a) + inner_product(x,x)))
    
    def condition_2(p:Integer, b:vector) -> bool: # type: ignore
        """
        Returns True if p divides inner_product(b,b)
        """
        return p.divides(inner_product(b,b))
    
    def condition_3(p:Integer, a:vector, b:vector) -> bool: # type: ignore
        """
        Returns True if p divides inner_product(b,a) + 1
        """
        return p.divides(inner_product(b,a) + 1)
        
    def select_vector_x(field:FiniteField, G:matrix) -> vector: # type: ignore
        """
        Selects a vector x from Fq^k such that x is not zero vector
        """
        n = G.ncols()       
        x =  random_vector_From(field, n)
        while x.is_zero():
            x =  random_vector_From(field, n)
        return x
    
    def select_vector_a(field:FiniteField, x:vector, r:int) -> vector: # type: ignore
        """
        Selects a vector a from Fq^r such that p divides inner_product(a,a) + inner_product(x,x)
        """
        a = random_vector_From(field, r)
        while not condition_1(field.characteristic(), a, x):
            a = random_vector_From(field, r)
        return a
    
    def select_vector_b(field:FiniteField, a:vector, r:int, max_iteration:int) -> vector: # type: ignore
        """
        Selects a vector b from Fq^r such that p divides inner_product(b,b) and p divides (inner_product(b,a) + 1)
        """
        b = random_vector_From(field, r)
        while not (condition_3(field.characteristic(), a, b) and condition_2(field.characteristic(), b)):
            b = random_vector_From(field, r)
            max_iteration -= 1
            if max_iteration <= 0:
                return None
        return b
    
    def select_a_b_x(field:FiniteField, G:matrix, r:int) -> (vector, vector, vector): # type: ignore
        """
        Selects a vector a, b, and x from Fq^r, Fq^r, and Fq^n respectively
        """
        x = select_vector_x(field, G)
        a = select_vector_a(field, x, r)
        b = select_vector_b(field, a, r, 100)
        while b is None:
            x = select_vector_x(field, G)
            a = select_vector_a(field, x, r)
            b = select_vector_b(field, a, r, 100)
            
        
        # sanity check all conditions
        assert condition_1(field.characteristic(), a, x)
        assert condition_2(field.characteristic(), b)
        assert condition_3(field.characteristic(), a, b)
        
        return a, b, x
    
    field = C.base_ring()
    p = C.base_ring().characteristic()
    G = C.generator_matrix()
    n = G.ncols()
    k = G.nrows()
    
    if n <= k:
        return C, f"{theorem_4_3_extended_const_method_generate_new_code_from.__name__} r = {r} skipped", (None, None, None)
    
    a, b, x = select_a_b_x(field, G, r)
    
    B = matrix.zero(field, k, r) # type: ignore
    
    for row in range(k):
        r_i = G[row]
        x_inner_product = inner_product(x, r_i)
        for col in range(r):
            b_i = b[col]
            B[row, col] = b_i * x_inner_product
    
    G_new = matrix(field, [x]).stack(G) # type: ignore
    a_stacked_B = matrix(field, [a]).stack(B)  # type: ignore
    G_new = a_stacked_B.augment(G_new)
    MS = MatrixSpace(field, k+1, n+r) # type: ignore
    new_code = LinearCode(MS(G_new))
    
    if not is_lcd_code(new_code):
        raise ValueError("Generated code is not an LCD code")
    
    return new_code, f"{theorem_4_3_extended_const_method_generate_new_code_from.__name__} r = {r}", (a, b, x)

def theorem_4_7_generate_new_code_from(C:LinearCode, m:int, r:int, max_iteration:int) -> Tuple[LinearCode,str, Tuple[Matrix, Matrix]]: # type: ignore
    """
    given a linear code C, returns a new linear code C' with [n+m, k+r]
    """
    
    if not is_lcd_code(C):
        raise ValueError("C is not an LCD code")
    
    field = C.base_ring()
    n = C.length()
    k = C.dimension()
    
    if n <= k:
        return C, f"{theorem_4_7_generate_new_code_from.__name__} m = {m}, r = {r} skipped", (None, None)
    
    G = C.generator_matrix()
    X = select_best_possible_sub_dual_matrix(C, r, max_iteration)
    if X is None:
        X = select_best_possible_sub_dual_matrix(C, r, max_iteration)
        
    
    if X is None:
        return C, f"{theorem_4_7_generate_new_code_from.__name__} m = {m}, r = {r} skipped", (None, None)
        
    A_MS = MatrixSpace(field, r, m) # type: ignore
    A = A_MS.random_element()
        
    if m > 0:
        singular =  (A*A.transpose() + X*X.transpose()).is_singular()
            
        while singular:
            A = A_MS.random_element()
            singular = (A*A.transpose() + X*X.transpose()).is_singular()

       
    A = A.stack(matrix.zero(field, k, m)) # type: ignore
    G_new = X.stack(G)
    G_new = A.augment(G_new)
    
    MS = MatrixSpace(field, k+r, n+m) # type: ignore
    new_code = LinearCode(MS(G_new))
    if not is_lcd_code(new_code):
        raise ValueError("Generated code is not an LCD code")
    return new_code, f"{theorem_4_7_generate_new_code_from.__name__} m = {m}, r = {r}", (A.rows(), X.rows())
    
def theorem_4_7_generate_new_code_from_2(C:LinearCode, r:int) -> Tuple[LinearCode,str]:
    """
    given a linear code C, returns a new linear code C' with [n, k+r]
    """
    field = C.base_ring()
    n = C.length()
    k = C.dimension()
    
    G = C.generator_matrix()
    dual_G = C.parity_check_matrix()
    
    X = dual_G[:r]  # r rows of the dual generator matrix   
    
    G_new = X.stack(G)
    
    MS = MatrixSpace(field, k+r, n) # type: ignore
    
    new_code = LinearCode(MS(G_new))
    if not is_lcd_code(new_code):
        raise ValueError("Generated code is not an LCD code")
    
    return new_code, f"{theorem_4_7_generate_new_code_from_2.__name__} r = {r}"


def theorem_slice_generator_matrix(C:LinearCode, r:int) -> Tuple[LinearCode,str]:
    """
    given a linear code C, returns a new linear code C' with [n, k+r]
    """
    field = C.base_ring()
    q = field.order()
    n = C.length()
    k = C.dimension()
    d = safe_minimum_distance(C)
    G = C.generator_matrix()
    
    def get_sliced_row(G:matrix, r:int) -> matrix:
        # deleted r rows where rows*rows^T non singular
        while True:
            deleted_rows = dict()
            while len(deleted_rows) < r:
                i = randint(0, G.nrows()-1)
                deleted_rows[i] = G[i]
                            
            d_matrix = matrix(deleted_rows.values())
            G_new = G.delete_rows(deleted_rows.keys())
            if not (G_new*G_new.transpose()).is_singular():
                return G_new
        
    
    G_new = get_sliced_row(G, r)
    
    new_code = LinearCode(G_new)
    if not is_lcd_code(new_code):
        raise ValueError("Generated code is not an LCD code")
    
    return new_code, f"{theorem_slice_generator_matrix.__name__} r = {r}"

# x = PolynomialRing(GF(3), 'x').gen()
# n=35
# gen_pol = x**25 + x**24 + x**23 + x**20 + x**19 + 2*x**18 + x**17 + x**16 + x**15 + x**14 + 2*x**13 + x**12 + 2*x**11 + 2*x**10 + 2*x**9 + 2*x**8 + x**7 + 2*x**6 + 2*x**5 + 2*x**2 + 2*x + 2
# cyclic_lcd_code = codes.CyclicCode(generator_pol=gen_pol, length=n)

# new_lcd_code_3 = shortened_code(cyclic_lcd_code, { 1})
# print(cyclic_lcd_code, new_lcd_code_3, safe_minimum_distance(cyclic_lcd_code), safe_minimum_distance(new_lcd_code_3), is_lcd_code(new_lcd_code_3))

# new_lcd_code_3, params = theorem_4_7_generate_new_code_from(cyclic_lcd_code, 0, 2)
# print(new_lcd_code_3, safe_minimum_distance(new_lcd_code_3))

# new_lcd_code_3, params = theorem_4_7_generate_new_code_from(cyclic_lcd_code, 1, 3)
# print(new_lcd_code_3, safe_minimum_distance(new_lcd_code_3))

# new_lcd_code_3, params = theorem_4_7_generate_new_code_from(cyclic_lcd_code, 2, 4)
# print(new_lcd_code_3, safe_minimum_distance(new_lcd_code_3))

# new_lcd_code_3, params = theorem_4_7_generate_new_code_from(cyclic_lcd_code, 1, 1)
# print(new_lcd_code_3, safe_minimum_distance(new_lcd_code_3))

# new_lcd_code_3, params = theorem_4_7_generate_new_code_from(cyclic_lcd_code, 2, 1)
# print(new_lcd_code_3, safe_minimum_distance(new_lcd_code_3))

# new_lcd_code_3, params = theorem_4_7_generate_new_code_from(cyclic_lcd_code, 3, 1)
# print(new_lcd_code_3, safe_minimum_distance(new_lcd_code_3))

# new_lcd_code_3, params = theorem_4_7_generate_new_code_from(cyclic_lcd_code, 3, 2)
# print(new_lcd_code_3, safe_minimum_distance(new_lcd_code_3))

# new_lcd_code_3, params = theorem_4_7_generate_new_code_from(cyclic_lcd_code, 2, 10)
# print(new_lcd_code_3, safe_minimum_distance(new_lcd_code_3))




# import random
# random.seed(0)

# for _ in range(100):
#     cyclic_code_record = get_random_lcd_code_q(3)
#     n = cyclic_code_record.n
#     cyclic_lcd_code = cyclic_code_record.to_sage_linear_code()
#     for i in range(n):
#         new_lcd_code_1 = lemma_4_1_generate_new_code_from(cyclic_lcd_code, i)

#         print(new_lcd_code_1, magma_session.magma.IsLCDCode(new_lcd_code_1), magma_session.magma.MinimumWeight(cyclic_lcd_code), magma_session.magma.MinimumWeight(new_lcd_code_1))

# for i in range(1, 100):
 #   new_lcd_code_1 = prop_4_2_generate_new_code_from(cyclic_lcd_code, 3)
 #   new_lcd_code_2 = theorem_4_3_extended_const_method_generate_new_code_from(cyclic_lcd_code, 30)
    # new_lcd_code_3 = theorem_4_7_generate_new_code_from(cyclic_lcd_code, 0, 1)

    # print(new_lcd_code_1, magma_session.magma.IsLCDCode(new_lcd_code_1), magma_session.magma.MinimumWeight(cyclic_lcd_code), magma_session.magma.MinimumWeight(new_lcd_code_1))
    # print(new_lcd_code_2, magma_session.magma.IsLCDCode(new_lcd_code_2), magma_session.magma.MinimumWeight(cyclic_lcd_code), magma_session.magma.MinimumWeight(new_lcd_code_2))
    # print(new_lcd_code_3, magma_session.magma.IsLCDCode(new_lcd_code_3), magma_session.magma.MinimumWeight(cyclic_lcd_code), magma_session.magma.MinimumWeight(new_lcd_code_3))

# from GenerateClosestLCDCode import get_lcd_codes_q

# bdlc_lcd_codes = [code  for code in get_bdlc_codes(2) if sqrt((code.n  - 40)**4 + (code.k- 21)**2) < 20]

# for lcd_code in bdlc_lcd_codes:
#     lcd_code_sage = lcd_code.to_sage_linear_code()
#     new_code,_ = theorem_slice_generator_matrix(lcd_code_sage, 2)
#     new_code_d =  safe_minimum_distance(new_code)
#     print(lcd_code, new_code,lcd_code.d,  new_code_d)
    

