# from re import M
# from sage.all import *
# from sage.coding.code_constructions import random_linear_code
# # from Utils.File_Cache import File_Cache
# # from Utils.Magma.BestDimensionLinearCode import BDLC
# # from Utils.Code_Utils import intersection_code, safe_minumum_distance

# # file_cache = File_Cache("Utils/Magma/BDLC_cache/bdlc_cache.json")

# # bdlc_provider = BDLC(file_cache, verbose=True)

# # print(bdlc_provider.get_dimension_of_bdlc(2, 4, 2))


# # F2 = GF(2)

# # # Define the first linear code C with generator matrix
# # C = codes.LinearCode(Matrix(F2, [[1, 0, 1, 0], [0, 1, 0, 1]]))

# # # Define the second linear code C2 with generator matrix
# # C2 = codes.LinearCode(Matrix(F2, [[1, 1, 1, 0], [0, 1, 0, 1]]))

# # int_code = intersection_code(C, C2)

# # print(int_code)


# # Read outputs LCD_Cyclic_Codes.json
# # output_cache = File_Cache("outputs/LCD_Cyclic_Codes.json")
# # output_cache_updated = File_Cache("outputs/LCD_Cyclic_Codes_updated.json")
# # values = output_cache.get_values()

# # for value in values:
# #     n = int(value['n'])
# #     k = int(value['k'])
# #     d = int(value['d'])
# #     gen_pol = value['gen_pol']
    
# #     if k>5 and k < n-5:
# #        output_cache_updated.set(f"LCD_Cyclic_Code_{n}_{k}_{d}", {'n':str(n), 'k':str(k), 'd':str(d), 'gen_pol':f"{gen_pol}" })

# # F2 = GF(2)

# # G = Matrix(F2, [[1,1, 1,0,0, 0]])
# # C = LinearCode(G)

# # print(safe_minumum_distance(C))

# m = 17
# F = FiniteField(2, 'a')
# R = PolynomialRing(F, 'Y')
# Y = R.gen()
# modulus = Y**m - 1
# factors = modulus.factor()

# generator_poly = max(factors, key=lambda x: x[0].degree())[0]

# extension_field = F.extension(generator_poly.degree(), 'z')

# alpha = extension_field.multiplicative_generator()
# zeta = alpha**((extension_field.order()-1)//m)

# c_coeffs = [1, 1, 1, 0, 0]

# def fourier_coefficients(coeffs, m, primitive_element):
#     return [sum([coeffs[g] * primitive_element**(g*h) for g in range(min(m, len(coeffs)))]) for h in range(m)]

# def inverse_fourier_coefficients(coeffs, m, primitive_element):
#     return [sum([coeffs[h] * primitive_element**(-g*h) for h in range(min(m, len(coeffs)))]) / m for g in range(m)]

# # print(fourier_coefficients(c_coeffs, m, zeta))

# # print(inverse_fourier_coefficients(fourier_coefficients(c_coeffs, m, zeta), m, zeta))

# #random_code = random_linear_code(F, 4, 2)

# Q = matrix(F, [
#     [0,1,1,0],
#     [0,0,1,1],
#     [1,0,0,1],
#     [1,1,0,0]
# ])
# I4 = identity_matrix(F, 4)

# G = I4.augment(Q)

# all_codewords = []
# for a0 in F:
#     for a1 in F:
#         for a2 in F:
#             for a3 in F:
#                 vec = vector(F, [a0,a1,a2,a3])  # dimension=4
#                 cw = vec * G
#                 all_codewords.append(cw)

# def trace_coeff(coeffs, m, primitive_element, L, F):
    
#     def _trace (c, L, F):
#         q = F.order()
#         t =  L.degree() // F.degree()
#         return sum([c**(q**i) for i in range(t)])
    
#     def inverse_fourier_coefficient(g):
#         s = F(0)
#         for h in range(len(coeffs)):
#             exponent = (-h*g)
#             s += _trace(coeffs[h] * primitive_element**exponent, L, F)
#         return s

    
#     return [inverse_fourier_coefficient(g) for g in range(m)]


# c_hat_coeffs = [fourier_coefficients(c, m, zeta) for c in all_codewords]

# print([inverse_fourier_coefficients(c, m, zeta) for c in c_hat_coeffs])
# print([trace_coeff(c, m, alpha, generator_poly, F) for c in c_hat_coeffs])
# y_vals_raw = [ [c.to_integer() for c in coeff] for coeff in c_hat_coeffs ]


# print(c_hat_coeffs)

# import matplotlib.pyplot as plt

# for i in range(len(y_vals_raw)):
#     colors = ['red', 'green', 'blue', 'orange', 'purple', 'black', 'yellow', 'pink', 'brown', 'cyan', 'magenta', 'grey', 'lightblue', 'lightgreen', 'lightcoral', 'lightcyan', 'lightgray', 'lightpink', 'lightsalmon', 'lightseagreen', 'lightskyblue', 'lightslategray', 'lightsteelblue', 'lightyellow']
#     scale = 1.0 / (2**len(y_vals_raw[0]) - 1)
#     plt.scatter(range(len(y_vals_raw[0])), y_vals_raw[i], color=colors[i], label=f"Code {i+1}")
# # plt.bar(range(m), y_vals, color="blue")

# plt.xlabel("Index h")
# plt.ylabel("Fourier Coeff as integer in [0..2^r-1]")
# plt.title("Fourier Coefficients in GF(2^r), displayed as integers")

# plt.savefig("fourier_coeffs.png")
# # for c in random_code:
# #     print(c)
# #     f_coeffs = fourier_coefficients(c, m, zeta)
# #     print(f_coeffs, inverse_fourier_coefficients(f_coeffs, m, zeta))

###################################################
# Example: Extend x to an orthonormal basis in R^3
###################################################
from Utils.Types import GeneratorMatrixRecord
from sage.all import *
from sage.coding.code_constructions import random_linear_code
# A = MatrixSpace(GF(2), 1, 3).random_element()
# X = MatrixSpace(GF(2), 1, 3).random_element()
# print(A.transpose() * A)

# random_code = random_linear_code(GF(2), 4, 2)
# g = random_code.generator_matrix()
# n = g.ncols()
# k = g.nrows()
# g_str_list = [row for row in g]

# print(GeneratorMatrixRecord(g))