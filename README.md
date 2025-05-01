# Extended LP Bound for LCD codes and New Binary and Ternary LCD Codes
This repository contains Linear Programming Bounds for LCD codes up to length 60 for binary codes (q=2) and up to length 50 for ternary codes (q=3). The repository also includes cyclic, quasi-cyclic, and computationally generated LCD codes. The generated LCD codes presented are potentially new since results are filtered using known codes and Best Known LCD Linear Codes from Magma V2.28-19.

## Requirements
- **SageMath**: Required for code analysis and generation.
- **Magma**: Essential for generating LCD and Quasi-Cyclic codes.
- **Gurobi**: Needed only for running integer linear programming (ILP).

## Repository Structure

- `outputs/`: Contains JSON files with systematically named LCD codes.
- `scripts/`: Code generation scripts used to produce and analyze the LCD codes.
- `KnownPaperResults/`: Known LCD code results from published papers.
- `LCDCodePool/`: Utilities for working with the LCD code pool.
- `LP/`: Scripts for integer linear programming related tasks.
- `Utils/`: Shared utilities across various scripts.

## Known Paper Results (`KnownPaperResults` Folder)
This folder contains the known results taken from the papers.
- `./KnownPaperResults/Stefka.py`: Gives a table for F_2 up to n=40
    - [Bouyuklieva, S. Optimal binary LCD codes. Des. Codes Cryptogr. 89, 2445–2461 (2021)](https://doi.org/10.1007/s10623-021-00929-w)

- `./KnownPaperResults/Wang.py`: Gives a table for F_2 up to n=50
    - [Guodong Wang and Shengwei Liu and Hongwei Liu(2024) New constructions of optimal binary LCD codes *Finite Fields and Their Applications*, 95](https://doi.org/10.1016/j.ffa.2024.102381)

- `./KnownPaperResults/YangLiu.py`: Gives a explicit calculation for F_2 when k=5
    - [Yang Liu, Ruihu Li, Qiang Fu, Hao Song. On the minimum distances of binary optimal LCD codes with dimension 5[J]. AIMS Mathematics, 2024, 9(7): 19137-19153.](https://doi.org/10.3934/math.2024933)

- `./KnownPaperResults/Harada.py`: Multiple paper used, gives various result for both F_2 and F_3. Naming convention is Harada_1, Harada_2, ...
    - `Harada_1`: [Harada, M. Construction of binary LCD codes, ternary LCD codes, and quaternary Hermitian LCD codes. Des. Codes Cryptogr. 89, 2295–2312 (2021)](https://doi.org/10.1007/s10623-021-00916-1)
    
    - `Harada_2`: [Araya, M., Harada, M., \& Saito, K. (2021). On the minimum weights of binary LCD codes and ternary LCD codes. Finite Fields and Their Applications, 76, 101925](https://doi.org/10.1016/j.ffa.2021.101925)

    - `Harada_3`: [Araya, M., Harada, M. \& Saito, K. Characterization and classification of optimal LCD codes. Des. Codes Cryptogr. 89, 617–640 (2021)](https://doi.org/10.1007/s10623-020-00834-8)
    
    - `Harada_4`: [M. Araya, M. Harada, K. Ishizuka and Y. Tanaka, "Characterizations of the Minimum Weights of LCD Codes of Large Dimensions," in IEEE Transactions on Information Theory, vol. 70, no. 12, pp. 8758-8769, Dec. 2024](https://doi.org/10.1109/TIT.2024.3483218)
    
    - `Harada_5`: [Araya, M., \& Harada, M. (2018). On the classification of linear complementary dual codes. Discrete Mathematics, 342(1), 270-278](https://doi.org10.1016/j.disc.2018.09.034)

    - `Harada_6`: [Harada, M., Saito, K. Binary linear complementary dual codes. Cryptogr. Commun. 11, 677–696 (2019)](https://doi.org/10.1007/s12095-018-0319-0)


    - `Harada_7`: [Araya, M., Harada, M. On the minimum weights of binary linear complementary dual codes. Cryptogr. Commun. 12, 285–300 (2020)](https://doi.org10.1007/s12095-019-00402-5)

- `./KnownPaperResults/ST_Dougherty_Ozkaya`: Gives a short cut calculation for k=1, and k= n-1
    - [S. T. Dougherty, J.-L. Kim, B. Özkaya, L. Sok, and P. Solé, "The combinatorics of LCD codes: Linear programming bound and orthogonal matrices" Int. J. Inf. Coding Theory, vol. 4, nos. 2–3, pp. 116–128, 2017.](https://doi.org/10.48550/arXiv.1506.01955)

- `./KnownResults/KnownResults.py`: Combines all the known results to create n/k table.

## LCD Code Pool (`LCDCodePool` Folder)
- `./LCDCodePool/GetClosestLCD.py`: Finds the closest LCD code using BDLC LCD, Cyclic and Quasi Cyclic Codes.
- `./LCDCodePool/LCD_Codes_to_Latex.py`: Creates the latex table for LCD Quasi Cyclic and Cyclic codes.

## Linear Programming (`LP` Folder)
- `./LP/Extended_ILP.py`: Integer linear programming solver (Non-LCD) 
- `./LP/Extended_LCD_ILP.py`: Integer LCD linear programming solver.
- `./LP/gurobi_tune.py`: Used for tuning the Gurobi model.
- `./LP/LP_to_Latex_table.py`: Used for creating latex table. 
- `./LP/LP_Utils.py`: Some utility functions used especially in ILP program.

## Utilities (`Utils` Folder)
Utilities used across the code baseç.
- `./Utils/CodeConstUtils/CodeConstUtils.py`: Implements the algebraic LCD generation algorithms presented in *Section 4*.

- `./Utils/Code_Utils.py`: Common utilities for codes.

- `./Utils/File_Cache.py`: Dictionary like buffered file read write entity.

- `./Utils/MagmaUtils.py`: Creates a local magma session which loads the magma codes under the folder `./Utils/Magma/MagmaCodes`.

- `./Utils/QuasiCyclicCode.py`: Implemets QuasiCyclic Code type, since SageMath does not have one.

- `./Utils/Types.py`: Provides strong types used across the code base.

- `./Utils/Magma/BestDimensionLinearCode.py`: Bulk BDLC LCD code getter using online Magma server.

- `./Utils/Magma/Invoke_Online_Command.py`: Invokes online magma command and parses them.


## LCD Cyclic Code Generation (LCD_Cyclic_Search.py)
LCD Cyclic code generator.

## LCD Quasi-Cyclic Code Generation (LCD_QuasiCyclic_Search.py)
LCD Quasi-Cyclic code generator.

## BDLC Code Search (BDLC_LCD_Search.py)
LCD BDLC code collector using online Magma Server via `./Utils/Magma/BestDimensionLinearCode.py`.

## LCD Code Generation (GenerateClosestLCDCode.py)
LCD Code code generator uses LCD Code Pool

## Output Files (Folder: outputs)
Contains Output Files of the programs
- `./outputs/code_generation_q2`: Generated LCD codes $`\in F_2`$.
- `./outputs/code_generation_q3`: Generated LCD codes $`\in F_3`$.

- `./outputs/LCD_Cyclic_Codes_q2.json`: Generated LCD cyclic codes $`\in F_2`$.
- `./outputs/LCD_Cyclic_Codes_q3.json`: Generated LCD cyclic codes $`\in F_3`$.

- `LCD_QuasiCyclic_Codes_q2.json`: Generated LCD Quasi-Cyclic codes $`\in F_2`$
- `LCD_QuasiCyclic_Codes_q3.json`: Generated LCD Quasi-Cyclic codes $`\in F_3`$

- `./outputs/LCD_ILP_output_q2_raw.csv`: ILP results before rounding down $`\in F_2`$.
- `./outputs/LCD_ILP_output_q2.csv`: ILP results after rounding down $`\in F_2`$.

- `./outputs/LCD_ILP_output_q3_raw.csv`: ILP results before rounding down $`\in F_3`$.
- `./outputs/LCD_ILP_output_q3.csv`: ILP results after rounding down $`\in F_3`$.


### Generated LCD codes Files Json File Structure

Each search entry has the key convention:
```
q_n_k_dmax
```
where:
- `q`: Cardinality of the finite field (e.g., 2 for binary, 3 for ternary).
- `n`: Length of the LCD code.
- `k`: Dimension of the LCD code.
- `dmax`: Upper bound for the minimum distance as derived from linear programming results.

Each JSON file provides comprehensive information about the generated code:

- `"code"`: Summary of the code parameters.
- `"GenMatrix"`: Generator matrix for constructing the code.
- `"min_distance"`: Minimum distance indicating the code's error-correcting capability.
- `"const_method_params"`: Theoretical method used for code construction.
- `"gen_objects"`: Parameters used during construction.
- `"parent_code"`: Hierarchical link to the parent code (if applicable).


