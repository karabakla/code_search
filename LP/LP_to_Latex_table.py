import csv
import os


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

for (n_min, n_max), (d_min, d_max) in n_d_list:

# n_min = 2
# n_max = 35

# d_min = 1
# d_max = 20


    output_array = [['0' for _ in range(n_max)] for _ in range(n_max)] 

        
    if os.path.exists(f"outputs/LCD_ILP_output_q{q}.csv"):
        with open(f"outputs/LCD_ILP_output_q{q}.csv", 'r') as file:
            reader = csv.reader(file)
            output_array = list(reader)

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

    def to_row_string(r:str):
        if '*' in r:
            return f"${r.rstrip('*')}^*$"
        
        if 'up' in r:
            return f"${r.rstrip('up')}^\\uparrow$"
            
        return r

    for _, n in enumerate(range(n_min-1, n_max)):
        if n < d_min :
            continue
        row= [ to_row_string(r) for r in output_array[n][d_min-1:d_max] if r != '0']
        
        latex_table += "\n" + " & ".join([ f"\\textbf{{{n+1}}}"] + row) + " &" * (d_max-len(row) - d_min +1) + " \\\\"

    table_name = "Binary" if q == 2 else "Ternary"
    
    latex_table += "\n\\hline"
    latex_table += "\n\\end{tabular}"
    latex_table += f"\n\\caption{{{table_name} LCD bounds for ${n_min} \\leq n \\leq {n_max}$ and ${d_min} \\leq d \\leq {d_max}$}}"
    latex_table += f"\n\\label{{tab:lp_tables_q{q}_{n_min}_{n_max}_{d_min}_{d_max}}}"
    latex_table += "\n\\end{sidewaystable}"
    #latex_table += "\n\\end{landscape}"


    with open(f"outputs/LCD_ILP_output_q{q}_{n_min}-{n_max}_{d_min}-{d_max}.tex", 'w') as file:
        file.write(latex_table)


