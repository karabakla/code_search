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