
from time import sleep
from typing import List, Set
from Utils.File_Cache import File_Cache
from Utils.Magma.BestDimensionLinearCode import BDLC
from Utils.Magma.Invoke_Online_Command import invoke_online_command
from Utils.Types import BdlcLcdCodeRecord, GeneratorMatrixRecord, LinearCodeRecord

def get_search_code(F, n_min, n_max, d_min, d_max):
    return f"""
        IsLCDCode := function (C)
            return C meet Dual(C) eq ZeroCode(BaseField(C), Length(C));
        end function;

        LcdCodes :=[];

        F := FiniteField({F});
        n_min := {n_min};
        n_max := {n_max};

        d_min := {d_min};
        d_max := {d_max};
    
        for n:= n_min to n_max do
            for d:= d_min to Min(d_max, n) do
                C := BDLC(F, n, d);
                if IsLCDCode(C) then
                //Append(~LcdCodes, C);
                printf "\\nBegin\\n[%o %o %o]\\n%o\\nEnd", Length(C), Dimension(C), MinimumDistance(C),  GeneratorMatrix(C);
                end if;
            end for;
        end for;
    """
    
# test = ['Begin', '[26 26 1]', '[1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]', '[0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]', '[0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]', '[0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]', '[0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]', '[0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]', '[0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]', '[0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]', '[0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]', '[0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]', '[0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]', '[0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0]', '[0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0]', '[0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0]', '[0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0]', '[0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0]', '[0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0]', '[0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0]', '[0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0]', '[0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0]', '[0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0]', '[0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0]', '[0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0]', '[0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0]', '[0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0]', '[0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]', 'End', 'Begin', '[26 13 7]', '[1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 1 1 1 1 0 0 1 0]', '[0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 1 1 1 1 0 0 1]', '[0 0 1 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 0 0 1 1 1 1 0 0]', '[0 0 0 1 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 0 0 1 1 1 1 0]', '[0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 0 0 1 1 1 1]', '[0 0 0 0 0 1 0 0 0 0 0 0 0 1 0 0 1 0 0 0 1 0 0 1 1 1]', '[0 0 0 0 0 0 1 0 0 0 0 0 0 1 1 0 0 1 0 0 0 1 0 0 1 1]', '[0 0 0 0 0 0 0 1 0 0 0 0 0 1 1 1 0 0 1 0 0 0 1 0 0 1]', '[0 0 0 0 0 0 0 0 1 0 0 0 0 1 1 1 1 0 0 1 0 0 0 1 0 0]', '[0 0 0 0 0 0 0 0 0 1 0 0 0 0 1 1 1 1 0 0 1 0 0 0 1 0]', '[0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 1 1 1 1 0 0 1 0 0 0 1]', '[0 0 0 0 0 0 0 0 0 0 0 1 0 1 0 0 1 1 1 1 0 0 1 0 0 0]', '[0 0 0 0 0 0 0 0 0 0 0 0 1 0 1 0 0 1 1 1 1 0 0 1 0 0]', 'End', 'Begin', '[26 12 8]', '[1 0 0 0 0 0 0 0 0 0 0 0 1 0 1 1 0 1 0 0 0 1 0 1 1 0]', '[0 1 0 0 0 0 0 0 0 0 0 0 1 0 1 0 1 1 1 0 0 1 1 1 0 1]', '[0 0 1 0 0 0 0 0 0 0 0 0 1 1 1 0 0 0 1 1 0 1 1 0 0 0]', '[0 0 0 1 0 0 0 0 0 0 0 0 1 0 0 0 0 1 0 1 1 1 1 0 1 0]', '[0 0 0 0 1 0 0 0 0 0 0 0 1 0 1 1 0 1 1 0 1 0 1 0 1 1]', '[0 0 0 0 0 1 0 0 0 0 0 0 1 1 1 0 1 1 1 1 0 0 0 0 1 1]', '[0 0 0 0 0 0 1 0 0 0 0 0 1 1 0 0 0 0 1 1 1 1 0 1 1 1]', '[0 0 0 0 0 0 0 1 0 0 0 0 1 1 0 1 0 1 0 1 1 0 1 1 0 1]', '[0 0 0 0 0 0 0 0 1 0 0 0 1 1 0 1 1 1 1 0 1 0 0 0 0 0]', '[0 0 0 0 0 0 0 0 0 1 0 0 1 0 0 1 1 0 1 1 0 0 0 1 1 0]', '[0 0 0 0 0 0 0 0 0 0 1 0 1 0 1 1 1 0 0 1 1 1 0 1 0 1]', '[0 0 0 0 0 0 0 0 0 0 0 1 1 1 1 0 1 0 0 0 1 0 1 1 0 0]', ...]


def parse_code_params(q:int, code:str) -> LinearCodeRecord:
    code_params = list(map(int, code.replace('[', '').replace(']', '').split()))
    return LinearCodeRecord(q, code_params[0], code_params[1], code_params[2])

def parse_search_code_results(q, results) -> Set[BdlcLcdCodeRecord]:
    codes:Set[BdlcLcdCodeRecord] = set()
    current_code:LinearCodeRecord|None = None
    current_generator_matrix_raw:List[str] = []
    for index, line in enumerate(results):
        if line == 'Begin':
            current_code = parse_code_params(q, results[index + 1])
        elif line == 'End':
            codes.add(BdlcLcdCodeRecord(current_code, GeneratorMatrixRecord(current_code.n, current_code.k, current_generator_matrix_raw[1:])))
            current_code = None
            current_generator_matrix_raw = []
        else:
            current_generator_matrix_raw.append(line)
    return codes

# test_result = parse_search_code_results(2, test)
# print(test_result)

def save_code(file:File_Cache, code:BdlcLcdCodeRecord):
    key = f"BDLC_LCD_Code_{code.q}_{code.n}_{code.k}_{code.d}"  
    file.set(key, code.to_json())

def is_code_exists(file:File_Cache, q:int, n:int, d:int) -> bool:
    values = file.get_values()
    for value in values:
        if value['n'] == n and value['d'] == d:
            return True
    return False

def main():
    q = 3
    n_min = 47
    n_max = 50
    d_min = 1
    
    batch_n = 1
    batch_d = 1
    
    calculated_codes = File_Cache(f"outputs/BDLC_LCD_Codes_q{q}.json")

    for batch_index_n in range(n_min, n_max+1, batch_n):
        n_begin = batch_index_n
        n_end = min((batch_index_n + batch_n - 1), n_max)

        for batch_index_d in range(d_min, n_end, batch_d):
            d_begin = batch_index_d
            d_end = min((batch_index_d + batch_d - 1), n_end)
            print(f"Searching for codes with n in [{n_begin}, {n_end}] and k in [{d_begin}, {d_end}]")
            result = invoke_online_command(get_search_code(q, n_begin, n_end, d_begin, d_end))
            codes = parse_search_code_results(q, result.get_results())
            for code in codes:
                save_code(calculated_codes, code)
            sleep(30)

       
        
    # result = invoke_online_command(get_search_code(2, 26, 26, 1, 20))
    
    # codes = parse_search_code_results(2, result.get_results())
    # print(codes)
    

if __name__ == '__main__':
    main()