import csv
import os

from KnownPaperResults.KnownResults import get_upper_bound_dimension
from Utils.File_Cache import File_Cache


q = 3


n_d_list_2 = [
    ((2, 30), (1, 29)),

    ((31, 60), (1, 29)),
    ((31, 60), (30, 60)),
]

n_d_list_3 = [
    ((2, 25), (1, 25)),

    ((26, 50), (1, 25)),
    ((26, 50), (26, 50)),
]


#####################
n_d_list = n_d_list_2 if q == 2 else n_d_list_3

upper_bound_file_cache = File_Cache(f"outputs/cache/code_tables_upper_bound_cache_q{q}.json", 10)
def get_upper_bound_dimension_cached(q:int, n:int, d:int):
    key = f"{q}_{n}_{d}"
    cached_value = upper_bound_file_cache.get(key)
    if cached_value is not None:
        return cached_value
    
    online_value = get_upper_bound_dimension(q,n,d)
    upper_bound_file_cache.set(key, online_value)
    
    return online_value

generated_lcd_codes = File_Cache(f"outputs/code_generation_complete_q{q}.json")
generated_lcd_cyclic_codes = File_Cache(f"LCDCodePool/LCD_Cyclic_Codes_q{q}.json")
generated_lcd_quasi_cyclic_codes = File_Cache(f"LCDCodePool/LCD_QuasiCyclic_Codes_q{q}.json")

def get_generated_lcd_codes_n_d_flat() -> dict[str, int]:
    ret:dict[str,int] = {}
    
    lcd_codes_keys = generated_lcd_codes.get_keys()
    
    for key in lcd_codes_keys:
        parts = key.split('_')
        q = int(parts[0])
        n = int(parts[1])        
        k = int(parts[2])        
        #d = generated_lcd_codes.get(key)["min_distance"] # type: ignore
        d = int(parts[3])
        
        dict_key = f"{q}_{n}_{d}"
        max_k = max(ret.get(key, k), k)
        ret[dict_key] = max_k
    
    return ret

generated_lcd_codes_n_d_flat = get_generated_lcd_codes_n_d_flat()


def get_lcd_code_dimension(q:int, n:int, k:int, d:int):
    if generated_lcd_cyclic_codes.contains(f"LCD_Cyclic_Code_{q}_{n}_{k}_{d}"):
        return k
        
    if generated_lcd_quasi_cyclic_codes.contains(f"LCD_quasi_Cyclic_Code{q}_{n}_{k}_{d}"):
        return k
    
    return generated_lcd_codes_n_d_flat.get(f"{q}_{n}_{d}")
           
            

# print(get_lcd_code_dimension(2, 33, 10, 4))

for (n_min, n_max), (d_min, d_max) in n_d_list:

# n_min = 2
# n_max = 35

# d_min = 1
# d_max = 20


    output_array = [['0' for _ in range(n_max)] for _ in range(n_max)] 

        
    with open(f"outputs/LCD_ILP_output_q{q}.csv", 'r') as file:
        reader = csv.reader(file)
        output_array = list(reader)
            
    # for n in range(len(output_array)):
    #     for d in range(len(output_array[0])):
    #         k = int(output_array[n][d].rstrip('*').rstrip('up'))
    #         k_low = int(output_array[n-1][d].rstrip('*').rstrip('up')) if n > 0 else int(output_array[n][d].rstrip('*').rstrip('up'))
    #         k_up = int(output_array[n][d-1].rstrip('*').rstrip('up')) if d > 0 else int(output_array[n][d].rstrip('*').rstrip('up'))
    #         if k < k_low:
    #             if output_array[n][d].endswith('*'):
    #                 print(f"Info: k decreased for n={n+1}, d={d+1}, but skipped: {k_low} -> {k}")
    #                 # output_array[n-1][d] = f"{k}"
    #             else:
    #                 output_array[n][d] = f"{get_upper_bound_dimension_cached(q, n, d)}" # type: ignore
    #                 print(f"Warning: k decreased for n={n+1}, d={d+1}: {k_low} -> {k}")
    
    # with open(f"outputs/LCD_ILP_output_q{q}_cleaned.csv", 'w', newline='') as file:
    #     writer = csv.writer(file)
    #     writer.writerows(output_array)
    
    # """
    latex_table = ""
    #latex_table = "\\begin{landscape}"
    #latex_table += "\n{"
    latex_table += "\n\\begin{sidewaystable}"
    latex_table += "\n\\smaller[2]"
    latex_table += "\n\\centering"
    latex_table += "\n\\setlength{\\tabcolsep}{4.5pt}"
    latex_table += "\n\\begin{tabular}{|c| " + "c " * (d_max-d_min +1) + "|}"
    latex_table += "\n\\hline"
    latex_table += "\n$n \\backslash  d$ & " + " & ".join([str(i) for i in range(d_min, d_max+1)]) + " \\\\"
    latex_table += "\n\\Xhline{4\\arrayrulewidth}"

    def get_upper_bound(n:int, d:int, k:int):
        return min(get_upper_bound_dimension_cached(q, n, d), k)
    
    def add_found_code_if_applicable(n:int, d:int, k:int):
        found_code_dim = get_lcd_code_dimension(q, n, k, d)
        if found_code_dim is None:
            return k
        
        if found_code_dim == k:
            return f"\\textbf{{{k}}}"
        
        if found_code_dim > k:
            return str(k)
        
        return f"{found_code_dim}-{k}"
    
    def to_row_string(n:int, k:str, d:int) -> str:
        if '*' in k:
            return f"${k.rstrip('*')}^*$"
        
        if 'up' in k:
            r_int = int(k.rstrip('up'))
            r_int = get_upper_bound(n, d, r_int)
            return f"${add_found_code_if_applicable(q,d, r_int)}^\\uparrow$"
        
        r_bounded = get_upper_bound(n, d, int(k))
        return str(add_found_code_if_applicable(n,d, r_bounded))       
    
    for _, n in enumerate(range(n_min-1, n_max)):
        if n < d_min :
            continue        
        
        if q == 2:
            output_array[n][n] = '1*' if (n+1) % 2 != 0 else '0*'
        elif q == 3:
            output_array[n][n] = '0*' if (n+1) % 3 == 0 else '1*'
        
        
        row = [ to_row_string(n+1, r, i + d_min) for i,r in enumerate(output_array[n][d_min-1:d_max]) if r != '0']
        
        latex_table += "\n" + " & ".join([ f"\\textbf{{{n+1}}}"] + row) + " &" * (d_max-len(row) - d_min +1) + " \\\\"

    table_name = "Binary" if q == 2 else "Ternary"
    
    latex_table += "\n\\hline"
    latex_table += "\n\\end{tabular}"
    latex_table += f"\n\\caption{{{table_name} LCD bounds for ${n_min} \\leq n \\leq {n_max}$ and ${d_min} \\leq d \\leq {d_max}$ \n \\\\ $*$ denotes skipped values; $\\uparrow$ indicates cases where the LP solver couldn't find a tighter upper bound; \\\\ explicitly found if written in bold.}}"
    latex_table += f"\n\\label{{tab:lp_tables_q{q}_{n_min}_{n_max}_{d_min}_{d_max}}}"
    latex_table += "\n\\end{sidewaystable}"
    #latex_table += "\n\\end{landscape}"


    with open(f"outputs/LCD_ILP_output_q{q}_{n_min}-{n_max}_{d_min}-{d_max}.tex", 'w') as file:
        file.write(latex_table)


