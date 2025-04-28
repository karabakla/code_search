from collections import deque
from typing import Tuple, Set
from Utils.Code_Utils import safe_minimum_distance
from Utils.MagmaUtils import MagmaSession
from sage.all import * # type: ignore
from sage.coding.linear_code import LinearCode # type: ignore
from sage.coding.code_constructions import *   # type: ignore

def is_lcd_code(C:LinearCode) -> bool:
    """
    Returns True if C is a Linear Complementary Dual (LCD) code, False otherwise.
    """
    G = C.generator_matrix()
    return not ((G * G.transpose()).is_singular())

 
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
    
