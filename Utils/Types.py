import ast
from typing import List, Optional, Tuple
from Utils.MagmaUtils import MagmaSession
from Utils.QuasiCyclicCode import QuasiCyclicCode
from sage.coding.linear_code import LinearCode # type: ignore
from sage.coding.cyclic_code import CyclicCode # type: ignore

from sage.all import GF, PolynomialRing, matrix, Matrix # type: ignore

class LinearCodeRecord:
    def __init__(self, q, n, k, d, is_lcd = False):
        self.q = int(q)
        self.n = int(n)
        self.k = int(k)
        self.d = int(d)
        self.is_lcd = is_lcd
        
    def is_zero_code(self):
        return self.k == 0 and self.d == self.n
    
    def __str__(self):
        return f"LinearCode [{self.n},{self.k},{self.d}]_{self.q}"
    def __repr__(self):
        return str(self)
    
    def __hash__(self) -> int:
        return hash(str(self))
    
    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.q == other.q and self.n == other.n and self.k == other.k and self.d == other.d
    
    # virtual method
    def to_sage_linear_code(self, magma_session:Optional[MagmaSession]) -> LinearCode: 
        raise NotImplementedError("to_sage_linear_code method is not implemented")
    
    def __lt__(self, other):
        return self.n < other.n or (self.n == other.n and self.k < other.k) or (self.n == other.n and self.k == other.k and self.d < other.d)
            
    
    def to_json(self):
        return {
            'q': self.q,
            'n': self.n,
            'k': self.k,
            'd': self.d,
            'is_lcd': self.is_lcd
        }
    
    @staticmethod
    def from_json(json):
        return LinearCodeRecord(json['q'], json['n'], json['k'], json['d'], json['is_lcd'])

class CyclicCodeRecord(LinearCodeRecord):
    def __init__(self, q, n, k, d, gen_pol, is_lcd = False):
        super().__init__(q, n, k, d, is_lcd)
        self.gen_pol = gen_pol
        
    def __str__(self):
        return f"CyclicCode [{self.n},{self.k},{self.d}]_{self.q}"
    def __repr__(self):
        return str(self)
    
    def __hash__(self) -> int:
        return hash(str(self))
    
    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.q == other.q and self.n == other.n and self.k == other.k and self.d == other.d and self.gen_pol == other.gen_pol

    def to_json(self):
        return {
            'q': self.q,
            'n': self.n,
            'k': self.k,
            'd': self.d,
            'gen_pol': f"{self.gen_pol}",
            'is_lcd': self.is_lcd
        }
    
    @staticmethod    
    def from_json(json):
        return CyclicCodeRecord(json['q'], json['n'], json['k'], json['d'], json['gen_pol'], json['is_lcd'])
    
    def to_sage_linear_code(self, magma_session:Optional[MagmaSession] = None) -> CyclicCode:
        P = PolynomialRing(GF(self.q), 'x')
        return CyclicCode(generator_pol=P(self.gen_pol), length=self.n)
    
class QuasiCyclicCodeRecord(LinearCodeRecord):
    def __init__(self, q, n, k, d, gen_pol_matrix_str, shift_degree, is_lcd):
        super().__init__(q, n, k, d, is_lcd)
        self.gen_pol_matrix_str:str = gen_pol_matrix_str
        self.shift_degree = int(shift_degree)
        
    def __str__(self):
        return f"QuasiCyclicCode [{self.n},{self.k},{self.d}]_{self.q}"
    def __repr__(self):
        return str(self)
    
    def __hash__(self) -> int:
        return hash(str(self))
    
    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.q == other.q and self.n == other.n and self.k == other.k and self.d == other.d and self.gen_pol_matrix_str == other.gen_pol_matrix_str and self.shift_degree == other.shift_degree

    def to_json(self):
        return {
            'q': self.q,
            'n': self.n,
            'k': self.k,
            'd': self.d,
            'gen_pol': f"{self.gen_pol_matrix_str}",
            'shift': self.shift_degree
        }
    
    @staticmethod    
    def from_json(json):
        return QuasiCyclicCodeRecord(json['q'], json['n'], json['k'], json['d'], json['gen_pol'], json['shift'], json['is_lcd']) 
    
    def to_sage_linear_code(self, magma_session:Optional[MagmaSession]) -> QuasiCyclicCode:
        if magma_session is None:
            raise Exception("Magma session is required to create QuasiCyclicCode")
        P = PolynomialRing(GF(self.q), 'x')
        gen_matrix_list_raw = ast.literal_eval(self.gen_pol_matrix_str)
        gen_matrix_list = [[P(pol) for pol in row] for row in gen_matrix_list_raw]

        return QuasiCyclicCode(magma_session, self.n, matrix(gen_matrix_list), self.shift_degree, self.is_lcd)
    
class GeneratorMatrixRecord:
    def __init__(self, n:int, k:int, generator_matrix_raw:List[str]): # type: ignore
        self.generator_matrix = self.__parse__(generator_matrix_raw)
        self.n = n
        self.k = k
        
        if len(self.generator_matrix) != k:
            raise Exception(f"Invalid generator matrix: {generator_matrix_raw}")
        
        if len(self.generator_matrix[0]) != n:
            raise Exception(f"Invalid generator matrix: {generator_matrix_raw}")
    
    def __init__(self, generator_matrix_raw:List[List[int]|Tuple[int]] | Matrix): # type: ignore
        self.generator_matrix = generator_matrix_raw
        if isinstance(generator_matrix_raw, List):
            self.n = len(generator_matrix_raw[0])
            self.k = len(generator_matrix_raw)
        else:
            self.n = generator_matrix_raw.ncols()
            self.k = generator_matrix_raw.nrows()
    
    def __parse_row__(self, row:str):
        return list(map(int, row.replace('[', '').replace(']', '').split()))
    
    def __comnbine_rows__(self, generator_matrix_raw:List[str]):
        """ if last row does not end with ] and next row does not start with [ then combine them """
        new_generator_matrix_raw = []
        i = 0
        while i < len(generator_matrix_raw):
            current_row = generator_matrix_raw[i]
            if current_row.endswith(']'):
                new_generator_matrix_raw.append(current_row)
                i += 1
                continue
            
            if (i + 1) < len(generator_matrix_raw) and not generator_matrix_raw[i + 1].startswith('['):
                combined_row = current_row + ' ' + generator_matrix_raw[i + 1]
                new_generator_matrix_raw.append(combined_row)
                i += 2
                continue
            
            raise Exception(f"Invalid generator matrix raw: {generator_matrix_raw}")
        return new_generator_matrix_raw
           
    def __parse__(self, generator_matrix_raw:List[str]):
        new_generator_matrix_raw = self.__comnbine_rows__(generator_matrix_raw)
        return [self.__parse_row__(row) for row in new_generator_matrix_raw]
     
    def __str__(self):
        return str(self.generator_matrix)
    
    def __repr__(self):
        return str(self)
    
    def to_json(self) -> dict:
        return str(self.generator_matrix).replace(',', '').replace('] ', '], ').replace('\n',', ') # type: ignore
    
    def __hash__(self) -> int:
        return hash(self.to_json())

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.to_json() == other.to_json()
       
    @staticmethod
    def from_json(matrix_json_str:str):
        rows_str = matrix_json_str.split('],')
        rows_str = [row.replace('[','').replace(']','') for row in rows_str]
        rows = [[int(r) for r in row.split(' ') if r.strip() != ''] for row in rows_str]
        return GeneratorMatrixRecord(rows) # type: ignore
                            
class BdlcLcdCodeRecord(LinearCodeRecord):
    def __init__(self, q:int, n:int, k:int, d:int, generator_matrix:GeneratorMatrixRecord):
        super().__init__(q, n, k, d)
        self.generator_matrix = generator_matrix       
    
    def __str__(self):
        return f"BDLC LCD Code [{self.n},{self.k},{self.d}]_{self.q}"
    
    def __repr__(self):
        return str(self)
    
    def to_json(self):
        return {
            'q': self.q,
            'n': self.n,
            'k': self.k,
            'd': self.d,
            'generator_matrix': self.generator_matrix.to_json()
        }
    
    def __hash__(self) -> int:
        return hash(str(self))
    
    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.q == other.q and self.n == other.n and self.k == other.k and self.d == other.d and self.generator_matrix == other.generator_matrix
        
    @staticmethod
    def from_json(json):
        return BdlcLcdCodeRecord(json['q'], json['n'], json['k'], json['d'], GeneratorMatrixRecord.from_json(json['generator_matrix']))
    
    def to_sage_linear_code(self, magma_session = None) -> LinearCode:
        return LinearCode(matrix(GF(self.q), self.generator_matrix.generator_matrix))
    

# test_matrix = GeneratorMatrixRecord(['[1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1', '1 1 1 1 1 1 1 1 1 1 1 1 1 1 1]'])
# test_matrix2 = GeneratorMatrixRecord(['[1 1 1 1 1 1 1 1 1 0 0 0 0 0 0 0 0 1 1 1 1 1 1 1 1 1]', '[0 0 0 0 0 0 0 0 0 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1]', '[0 0 0 0 0 0 0 0 0 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1]' ])
# print(test_matrix.generator_matrix)
# print(test_matrix2.generator_matrix)