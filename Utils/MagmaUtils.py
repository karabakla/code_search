from operator import ge
import os
from sage.all import *
from sage.coding.linear_code import *
from sage.coding.cyclic_code import *
from sage.interfaces.magma import Magma

class MagmaSession:
    def __init__(self, workspace:str|None=None, thread_count=1):
        self.magma = Magma()
        # make sure that the magma code is attached
        SAGE_EXTCODE = SAGE_ENV['SAGE_EXTCODE'] 
        self.magma.attach('%s/magma/sage/basic.m'%SAGE_EXTCODE)
        #self._magma._start()
        self.magma.eval(f"SetNthreads({thread_count});")
        if workspace is not None:
            self.__attach_workspace__(workspace)
                
    def __attach_file__(self, file_path):
        self.magma.eval(f"Attach(\"{file_path}\");")
    
    def __attach_workspace__(self, folder_path):
        for file in os.listdir(folder_path):
            if file.endswith(".m"):
                self.__attach_file__(os.path.join(folder_path, file))
           
            
    def generate_random_lcd_code(self, base_field, length, dimension):
        """
        Generate a random linear complementary dual code.
        
        Parameters:
        base_field -- The base field of the code
        length -- The length of the code
        dimension -- The dimension of the code
        
        Returns:
        A random linear complementary dual code.
        """
        lcd_code_magma = self.magma.GenerateRandomLCDCode(base_field, length, dimension)
        converted_code = self.__from_magma_linear_code__(base_field, lcd_code_magma)
        del lcd_code_magma
        
        return converted_code
        
    

class MagmaSageConverter:
    @staticmethod
    def __is_magma_linear_code__(magma_linear_code):
        # '[10, 5, 1] Linear Code over GF(2)\nGenerator matrix:\n[1 0 0 0 0 0 0 0 0 0]\n[0 1 0 1 0 0 0 0 0 0]\n[0 0 1 1 1 0 1 0 0 1]\n[0 0 0 0 0 1 0 1 0 1]\n[0 0 0 0 0 0 0 0 1 1]'
        # '[7, 4, 3] Cyclic Linear Code over GF(2)\nGenerator matrix:\n[1 0 0 0 1 1 0]\n[0 1 0 0 0 1 1]\n[0 0 1 0 1 1 1]\n[0 0 0 1 1 0 1]'
        magma_linear_code_str = str(magma_linear_code)
        lines = magma_linear_code_str.split("\n")
        if "Linear Code" not in lines[0]:
            return None, None, None, None, None
        
        is_cyclic = "Cyclic" in lines[0]
        
        code_descriptions = lines[0].split(']')[0].replace('[', '').replace(']', '').split(',')
        n = int(code_descriptions[0])
        k = int(code_descriptions[1])
        d = int(code_descriptions[2])
        field = eval(lines[0].split(']')[1].split(' ')[-1])
        generator_matrix = [list(map(int, line.replace('[', '').replace(']', '').split(' '))) for line in lines[2:]]
        
        if is_cyclic:
            return "Cyclic", n, k, d, field, generator_matrix
        return "Linear", n, k, d, field, generator_matrix
        
    @staticmethod
    def __from_magma_linear_code__(magma_linear_code):
        code_type, n, k, d, field, generator_matrix = MagmaSageConverter.__is_magma_linear_code__(magma_linear_code)
        if code_type is None:
            return None
        
        linear_code = LinearCode(Matrix(field, generator_matrix))
        if code_type == "Cyclic":
            return CyclicCode(code=linear_code)
        return linear_code

    @staticmethod
    def from_magma_linear_code(magma_linear_code):
        return MagmaSageConverter.__from_magma_linear_code__(magma_linear_code)
    
# magma_session = MagmaSession(f"{os.getcwd()}/Utils/Magma/MagmaCodes")

# print(magma_session.magma.GenerateLinearCodeReciprocalPairs(GF(2), 10, 5, 10, nvals = 2))
# magma_session.set_seed(0)
# from sage.coding.code_constructions import random_linear_code

# lcd_code = magma_session.GenerateRandomLCDCode(GF(2), 10, 5)
# print(MagmaSageConverter.from_magma_linear_code(lcd_code))

# for i in range(100):
#     _m = MagmaSession(f"{os.getcwd()}/Utils/Magma/MagmaCodes")
#     print(_m.GenerateRandomLCDCode(GF(2), 10, 5))