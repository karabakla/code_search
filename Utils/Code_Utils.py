from math import e
from sage.all import * # type: ignore
from sage.coding.linear_code import LinearCode # type: ignore
from sage.coding.code_constructions import random_linear_code # type: ignore
from sage.all import Polynomial, magma # type: ignore
import numpy as np # type: ignore

def zero_code(F, n):
    """
    Generate the zero code over a finite field F.
    
    Parameters:
    F -- A finite field
    n -- The length of the code
    
    Returns:
    The zero code over the field F with length n.
    """
    return LinearCode(Matrix(F, 0, n))

def intersection_code(A, B):
    # Check if the codes have the same length
    if A.length() != B.length() or A.base_field() != B.base_field():
        raise ValueError("The two codes must be over the same field and have the same length.")

    # Create a generator matrix for the intersection code
    generator_matrix_list = []
    for generator in A.generator_matrix():
        if generator in B.generator_matrix():
            generator_matrix_list.append(generator)

    generator_matrix = Matrix(A.base_field(), generator_matrix_list)
    
    # Zero code
    if generator_matrix.nrows() == 0:
        return LinearCode(Matrix(A.base_field(), 0, A.length()))
    
    # Create the intersection code using the generator matrix
    intersection_code = LinearCode(generator_matrix)

    return intersection_code

def hermitian_inner_product(x, y, q):
    """
    Compute the Hermitian inner product of two vectors x and y over GF(q^2).
    
    Parameters:
    x -- A vector over GF(q^2)
    y -- A vector over GF(q^2)
    q -- The size of the base field GF(q)
    
    Returns:
    The Hermitian inner product of x and y over GF(q^2).
    """
    # Check that the vectors have the same length
    if len(x) != len(y):
        raise ValueError("Vectors must have the same length.")
    
    # Compute the Hermitian inner product
    return sum([x[i] * y[i]**q for i in range(len(x))])

def hermitian_dual_code(C):
    
    if C.dimension() == 0:
        return LinearCode(Matrix(C.base_field(), 0, C.length()))
    
    Fq2 = C.base_field()
    q = int(sqrt(Fq2.order()))  # q is the base field size #type: ignore
    n = C.length()
    
    hermitian_dual = []
    for v in Fq2**n:
        is_hermitian = True
        for c in C:
            if hermitian_inner_product(c, v, q) != 0:
                is_hermitian = False
                break
        if is_hermitian:
            hermitian_dual.append(v)

    # If the dual code is empty, return the zero code
    if (len(hermitian_dual) == 1 and all([x == 0 for x in hermitian_dual[0]])) or len(hermitian_dual) == 0:
        return LinearCode(Matrix(Fq2, 0, n))
    
    return LinearCode(Matrix(Fq2, hermitian_dual))
        
# def is_LCD_code(C):
    """
    Check if a linear code is a linear complementary dual code.
    
    Parameters:
    C -- A linear code
    
    Returns:
    True if the code is a linear complementary dual code, False otherwise.
    """
    
    dual_C = C.dual_code()
    intersection_C = intersection_code(C, dual_C)
    return is_zero_code(intersection_C)    

def is_hermitian_LCD_code(C):
    """
    Check if a linear code is a Hermitian linear complementary dual code.
    
    Parameters:
    C -- A linear code
    
    Returns:
    True if the code is a Hermitian linear complementary dual code, False otherwise.
    """
    
    hermitian_dual = hermitian_dual_code(C)
    
    intersection_C = intersection_code(C, hermitian_dual)
    return is_zero_code(intersection_C)

def vertical_concatanate_codes(C1, C2):
    """
    Concatenate two linear codes.
    
    Parameters:
    C1 -- A linear code
    C2 -- A linear code
    
    Returns:
    The concatenated code of C1 and C2.
    """
    # Check if the codes have the same length
    if C1.length() != C2.length():
        raise ValueError("The two codes must have the same length.")
    
    c1_generator_matrix = C1.generator_matrix()
    
    if c1_generator_matrix.nrows() == 0:
        return C2
    c2_generator_matrix = C2.generator_matrix()
    
    # for row in c2_generator_matrix:
    #     c1_generator_matrix = c1_generator_matrix.stack(row)
    
    # Create a generator matrix for the concatenated code
    generator_matrix = c1_generator_matrix.stack(c2_generator_matrix)
    
    # Create the concatenated code using the generator matrix
    concatenated_code = LinearCode(generator_matrix)
    
    return concatenated_code

def calculate_min_distance(code_word_list):
    """
    Calculate the minimum distance of a linear code.
    
    Parameters:
    code_word_list -- A list of codewords
    
    Returns:
    The minimum distance of the code.
    """
    # Initialize the minimum distance to the length of the code
    min_distance = len(code_word_list[0])
    
    # Iterate over all pairs of codewords
    for i in range(len(code_word_list)):
        for j in range(i + 1, len(code_word_list)):
            # Compute the Hamming distance between the codewords
            distance = sum([code_word_list[i][k] != code_word_list[j][k] for k in range(len(code_word_list[i]))])
            
            # Update the minimum distance if necessary
            if distance < min_distance:
                min_distance = distance
    
    return min_distance

def safe_minimum_distance(C):
    """
    Sagemath minimum distance function is not reliable for some cases.
    This function is a safe alternative to calculate the minimum distance of a linear code.
    """
    # zero code
    if C.dimension() == 0:
        return C.length()

    try:   
        if C.dimension() <= 5:
            return min(c.hamming_weight() for c in C if not c.is_zero())
    except:
        pass
    try:
        return C.minimum_distance(algorithm='guava')
    except:
        pass
    try:
        return C.minimum_distance()
    except:
        pass

    return magma.MinimumWeight(C).sage()

def is_zero_code(C):
    """
    Check if a linear code is the zero code.
    
    Parameters:
    C -- A linear code
    
    Returns:
    True if the code is the zero code, False otherwise.
    """
    return C.dimension() == 0 and safe_minimum_distance(C) == C.length()

def root_of_unity(n, K):
    """
    Return a primitive n-th root of unity in the smallest possible extension field of K.

    Parameters:
    n : int
        The integer n specifying the order of the root of unity.
    K : FiniteField
        The base finite field.

    Returns:
    FldFinElt
        A primitive n-th root of unity in the smallest possible extension field of K.
    """
    # Ensure n is a positive integer
    if n <= 0:
        raise ValueError("n must be a positive integer.")
    
    # Create the smallest extension field of K containing a primitive n-th root of unity
    q = K.characteristic()
    if gcd(n, q) != 1:
        raise ValueError("n must be coprime to the characteristic of K.")
    
    # q^m = 1 mod n and m is minimal
    for m in range(1, n):
        if q**m % n == 1:
            return K.extension(m, 'w').primitive_element()**((q**m - 1)/n)
    else:
        raise ValueError("No suitable extension field exists.")

def to_monic_reciprocal_polynomial(f:Polynomial) -> Polynomial:
    """
    Convert a polynomial to its reciprocal polynomial.
    
    Parameters:
    f -- A polynomial
    
    Returns:
    The reciprocal polynomial of f.
    """
    return f.reverse().monic() 

def is_self_reciprocal_polynomial(f):
    return f.monic() == to_monic_reciprocal_polynomial(f)

#print(rootOfUnity(5, GF(2)).parent())
# F2 = GF(2)
# #C = LinearCode(Matrix(F2, [[1,1,1,0,0,0],[0,0,0,1,0,0],[0,0,0,0,1,0],[0,0,0,0,0,1]]))

# C = LinearCode(Matrix(F2, [[1,0,0,0,0,0],[0,1,0,0,0,0],[0,0,1,0,0,0],[0,0,0,1,0,1],[0,0,0,0,1,1]]))
# print(is_quasi_cyclic(C, 2))