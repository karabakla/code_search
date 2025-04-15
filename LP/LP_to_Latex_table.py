import csv
import os

n_min = 26
n_max = 50

d_min = 1
d_max = 26

q = 3

output_array = [['0' for _ in range(n_max)] for _ in range(n_max)] 

    
if os.path.exists(f"outputs/LCD_ILP_output_{q}.csv"):
    with open(f"outputs/LCD_ILP_output_{q}.csv", 'r') as file:
        reader = csv.reader(file)
        output_array = list(reader)


# """
# \begin{center}
# \begin{sidewaystable}
# \begin{tabular}{|c c c c c c c c c c c c|}
# \hline
# $n \backslash  d$ & 1 & 2 & 3 & 4 & 5 & 6 & 7 & 8  \\

# \Xhline{4\arrayrulewidth}

# \end{tabular}
# \captionof{table}{A wide table in landscape orientation.}
# \label{tab:lp_tables}
# \end{sidewaystable}
# \end{center}

# """
latex_table = "\\begin{landscape}"
latex_table += "\n{\\smaller[2]"
latex_table += "\n\\begin{table}"
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

latex_table += "\n\\hline"
latex_table += "\n\\end{tabular}"
latex_table += f"\n\\caption{{Ternary LCD bounds for ${n_min} \\leq n \\leq {n_max}$ and ${d_min} \\leq d \\leq {d_max}$}}"
latex_table += f"\n\\label{{tab:lp_tables_q{q}_{n_min}_{n_max}_{d_min}_{d_max}}}"
latex_table += "\n\\end{table} \n}"
latex_table += "\n\\end{landscape}"


with open(f"outputs/LCD_ILP_output_{q}.tex", 'w') as file:
    file.write(latex_table)


