from sage.coding.linear_code import LinearCode
from sage.matrix.constructor import Matrix
from sage.all import *

def trace(x, F):
    
    x_field_degree = x.parent().degree()
    base_field_degree = F.degree()
    
    # if not (x in F):
    #     raise ValueError("The element must be in the field")
    
    q = F.order()
    m =  x_field_degree // base_field_degree
            
    return sum([x**(q**i) for i in range(m)])


# not working yet
def trace_expansion_code(C, F0, n, alpha):
    # Get the base field of the code
    F = C.base_ring()
    F1 = alpha.parent()

    if C.dimension() == 0:
        return LinearCode(Matrix(F0, 0, n * C.length())), []

    if len(F) % len(F0) != 0:
        raise ValueError("The field F0 must be a subfield of the alphabet of the code C")

    if len(F) % len(F1) != 0:
        raise ValueError("The element alpha must lie in a subfield of the alphabet of the code C")

    # Determine the degree
    m = F.degree() // F0.degree()
    basis = [alpha**i for i in range(m)]
    
    gens = C.gens()
    
    # G_raw = []
    # for g in gens:
    #     for b in basis:
    #         row = []
    #         for a in g:
    #             for k in range(n):
    #                 trace_result = trace(a * b * alpha**(-k), F0)
    #                 row.append(trace_result)
    #         G_raw.append(row)
    

    # Construct the generator matrix
    G = Matrix(F0, [[trace(a * b * alpha**(-k), F0) for a in g for k in range(n)] 
                     for b in basis for g in C.gens()])
    
    if all([x == 0 for x in G]):
        return LinearCode(Matrix(F0, 0, n * C.length())), []
    return LinearCode(G), G

# F2 = GF(2)

# C = LinearCode(Matrix(GF(2), [[1, 0], [0, 1]]))

# m = 9

# F9 = FiniteField(9)
# F3 = FiniteField(3)
# alpha = F2(1)
# #print(trace(alpha, F3))
# print(trace_expansion_code(C, F2, m, alpha))

