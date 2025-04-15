# since sage does not support quasi-cyclic codes, we will use magma to generate the quasi-cyclic codes

from typing import Tuple
import os
from Utils.MagmaUtils import MagmaSession
from sage.interfaces.magma import Magma # type: ignore
from sage.coding.linear_code import LinearCode # type: ignore
from sage.matrix.constructor import Matrix # type: ignore
from sage.rings.integer import Integer # type: ignore
from sage.all import divisors, vector # type: ignore

def _to_polynomial_list(gen_pol:Matrix):
    return [ x for xs in gen_pol for x in xs]


class QuasiCyclicCode(LinearCode):
    #__magma_session = create_magma_session(12)
    
    def __init__(self, magma_session:MagmaSession, n:int, gen_pol_matrix:Matrix, shift_degree:int, is_lcd:bool):
        self.n = Integer(n)
        self.shift_degree = Integer(shift_degree)
        self.gen_pol_matrix = gen_pol_matrix
        self.is_lcd = is_lcd
        self._height = self.gen_pol_matrix.nrows()

        for _ in range(100):
            try:
                _generator_matrix, _shift_degree  = QuasiCyclicCode.__try_init__(magma_session, n, _to_polynomial_list(gen_pol_matrix), self._height, shift_degree, is_lcd)
                self._generator_matrix = _generator_matrix # type: ignore
                self.shift_degree = _shift_degree
                super().__init__(self._generator_matrix)
                return
            except:
                pass
            
        raise Exception("Could not generate quasi-cyclic code")

    @staticmethod
    def __try_init__(magma_session:MagmaSession, n:int, generator_pol_flat, height,  shift_degree:int, is_lcd:bool) -> Tuple[Matrix,int]: # type: ignore
        _magma_code = magma_session.magma.QuasiCyclicCode(n, generator_pol_flat, height)
        _generator_matrix:Matrix = _magma_code.GeneratorMatrix().sage()
                
        if shift_degree <= 1:
            for m in divisors(n):
                if m != n and _magma_code.IsQuasiCyclic(m):
                    shift_degree = m
                    break
        
        del _magma_code
        return (_generator_matrix, shift_degree) # type: ignore
    
    def __str__(self):
        return f"[{self.n}, {self.dimension()}] Quasi Cyclic Linear Code  Shift Degree: {self.shift_degree} LCD: {self.is_lcd}"
    
    def __repr__(self):
        return self.__str__()
    
    def __eq__(self, other):
        return isinstance(other, QuasiCyclicCode) and self.n == other.n and self.gen_pol_matrix == other.gen_pol_matrix and self.shift_degree == other.shift_degree and self.is_lcd == other.is_lcd
    
    def __hash__(self):
        return hash((self.n, self.gen_pol_matrix, self.shift_degree, self.is_lcd))
            
    def __json__(self):
        return {
            "n": self.n,
            "gen_pol_matrix": self.gen_pol,
            "shift_degree": self.shift_degree,
            "is_lcd": self.is_lcd
        }
    
    def generator_matrix(self): # type: ignore
        return self._generator_matrix
# from sage.all import GF, PolynomialRing
# P = PolynomialRing(GF(2), 'x')
# x = P.gen()
# G = Matrix([[x + 1, 0, x**7 + x**6 + x**5 + x**2], [0, x + 1, x**5 + x**3 + x + 1]])

# qc = QuasiCyclicCode(27, G, 1, True)

# print(qc)