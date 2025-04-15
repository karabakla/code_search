from GetClosestLCD import *
from KnownPaperResults import KnownResults

def create_magma_session(thread_count = 12):
    magma_session = MagmaSession(f"{os.getcwd()}/Utils/Magma/MagmaCodes", thread_count)
    magma_session.magma.set_seed(0)
    return magma_session

def latex_cyclic_code(q:int):
    
    cyclic_codes = get_cyclic_codes(q)

    cyclic_code_set = set()
    for cyclic_code in cyclic_codes:
        n = cyclic_code.n
        k = cyclic_code.k
        d = cyclic_code.d
        cyclic_code_set.add((n, k, d))

    latex_output = "\\begin{align*}\n"
    item = "&"
    code_per_item = 7
    for index, (n, k, d) in enumerate(sorted(cyclic_code_set)):
        code = f"[{n},\\ {k},\\ {d}]"
        item += code + ",\\ "
        if (index+1) % code_per_item == 0:
            latex_output += f"{item.rstrip(',\\ ')}&& \\\\\n"
            item = "&"

    if item != "&":
        latex_output += f"{item.rstrip(',\\ ')} \\\\\n"
    
    latex_output += "\\end{align*}"

    # copy to clipboard
    print(latex_output)

    import pyperclip
    pyperclip.copy(latex_output)

#latex_cyclic_code(3)

def should_skip(q, n ,k ):
    known_result = KnownResults.get_largest_min_distance(q, n, k)
    if isinstance(known_result, int):
        return True
    if isinstance(known_result, str):
        return known_result.isdecimal()
    
    bdlc_codes = get_bdlc_codes(q)
    
    if any([c.n == n and c.k == k for c in bdlc_codes]):
        return True
    
    return False
        

def latex_quasi_cyclic_code(q:int):
    quasi_cyclic_codes = get_quasi_cyclic_codes(q)

    quasi_cyclic_code_set = set()
    for quasi_cyclic_code in quasi_cyclic_codes:
        n = quasi_cyclic_code.n
        k = quasi_cyclic_code.k
        d = quasi_cyclic_code.d
        quasi_cyclic_code_set.add((n, k, d))

    latex_output = "\\begin{align*}\n"
    item = "&"
    code_per_item = 7
    for index, (n, k, d) in enumerate(sorted(quasi_cyclic_code_set)):
        
        if should_skip(q, n, k):
            continue
        
        code = f"[{n},\\ {k},\\ {d}]"
        item += code + ",\\ "
        if (index+1) % code_per_item == 0:
            latex_output += f"{item.rstrip(',\\ ')} \\\\\n"
            item = "&"
    
    if item != "&":
        latex_output += f"{item.rstrip(',\\ ')} \\\\\n"

    latex_output += "\\end{align*}"

    # copy to clipboard
    print(latex_output)

    import pyperclip
    pyperclip.copy(latex_output)
    
latex_quasi_cyclic_code(3)