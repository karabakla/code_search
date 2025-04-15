import json
import os
import random
from typing import Callable, Optional, Set
from Utils.MagmaUtils import MagmaSession
from Utils.Types import BdlcLcdCodeRecord, CyclicCodeRecord, LinearCodeRecord, QuasiCyclicCodeRecord

from sage.coding.linear_code import LinearCode # type: ignore
from sage.coding.cyclic_code import CyclicCode # type: ignore

# def create_magma_session(thread_count = 1):
#     magma_session = MagmaSession(f"{os.getcwd()}/Utils/Magma/MagmaCodes", thread_count)
#     magma_session.magma.set_seed(0)
#     return magma_session

def _get_cyclic_codes(cyclic_codes_json_file:str) -> Set[CyclicCodeRecord]:       
    with open(cyclic_codes_json_file, 'r') as f:
        json_data = json.loads(f.read())
        records:Set[CyclicCodeRecord] = set()
       
        for record_key in json_data:
            _record = json_data[record_key]
            q = _record["q"]
            n = _record["n"]
            k = _record["k"]
            d = _record["d"]
            is_lcd = _record["is_lcd"]
            gen_pols = _record["gen_pols"]
            for gen_pol in gen_pols:
                records.add(CyclicCodeRecord(q, n, k, d, gen_pol, is_lcd))
        
        for each in records:
            code_sage = each.to_sage_linear_code()
            G = code_sage.generator_matrix()
            is_lcd = not (G*G.transpose()).is_singular()
            if each.is_lcd and not is_lcd:
                raise Exception("Error Loading Quasi Cyclic Codes")
        
        return records
    
    raise Exception("Error Loading Cyclic Codes")

def _get_quasi_cyclic_codes(quasi_cyclic_codes_json_file:str, magma_session:Optional[MagmaSession] = None) -> Set[QuasiCyclicCodeRecord]:
        
    with open(quasi_cyclic_codes_json_file, 'r') as f:
        json_data = json.loads(f.read())
        records:Set[QuasiCyclicCodeRecord] = set()
       
        for record_key in json_data:
            _record = json_data[record_key]
            q = _record["q"]
            n = _record["n"]
            k = _record["k"]
            d = _record["d"]
            is_lcd = _record["is_lcd"]
            gen_pols = _record["gen_pols"]
            for gen_pol_raw in gen_pols:
                gen_pol_record = gen_pol_raw.split(', [[')
                shift_degree = int(gen_pol_record[0].split(':')[1])
                gen_pol = f"[[{gen_pol_record[1]}"
                records.add(QuasiCyclicCodeRecord(q, n, k, d, gen_pol,shift_degree, is_lcd))
        
        if magma_session is not None:
            for each in records:
                code_sage = each.to_sage_linear_code(magma_session)
                G = code_sage.generator_matrix()
                is_lcd = not (G*G.transpose()).is_singular()
                if each.is_lcd and not is_lcd:
                    raise Exception("Error Loading Quasi Cyclic Codes")
            
        return records
    
    raise Exception("Error Loading Quasi Cyclic Codes")

def _get_bdlc_lcd_codes(bdlc_lcd_codes_json_file:str) -> Set[BdlcLcdCodeRecord]:    
    with open(bdlc_lcd_codes_json_file, 'r') as f:
        json_data = json.load(f)
        records:Set[BdlcLcdCodeRecord] = {BdlcLcdCodeRecord.from_json(record) for record in json_data.values()}
        
        for each in records:
            code_sage = each.to_sage_linear_code()
            G = code_sage.generator_matrix()
            is_lcd = not (G*G.transpose()).is_singular()
            if each.is_lcd and not is_lcd:
                raise Exception("Error Loading Quasi Cyclic Codes")
        
        return records
    
    raise Exception("Error Loading BDLC LCD Codes")

def get_cyclic_codes(q:int) -> Set[CyclicCodeRecord]:
    if q == 2:
        return _get_cyclic_codes("LCDCodePool/LCD_Cyclic_Codes_q2.json")
    return _get_cyclic_codes("LCDCodePool/LCD_Cyclic_Codes_q3.json")

def get_bdlc_codes(q:int) -> Set[BdlcLcdCodeRecord]:
    if q == 2:
        return _get_bdlc_lcd_codes("LCDCodePool/BDLC_LCD_Codes_q2.json")
    return _get_bdlc_lcd_codes("LCDCodePool/BDLC_LCD_Codes_q3.json")

def get_quasi_cyclic_codes(q:int, magma_session:Optional[MagmaSession] = None) -> Set[QuasiCyclicCodeRecord]:
    if q == 2:
        return _get_quasi_cyclic_codes("LCDCodePool/LCD_QuasiCyclic_Codes_q2.json", magma_session)
    return _get_quasi_cyclic_codes("LCDCodePool/LCD_QuasiCyclic_Codes_q3.json", magma_session)

def get_lcd_codes_q(magma_session:MagmaSession, q:int) -> Set[CyclicCodeRecord | QuasiCyclicCodeRecord | BdlcLcdCodeRecord]:
    cyclic_codes = get_cyclic_codes(q)
    quasi_cyclic_codes = get_quasi_cyclic_codes(q, magma_session)
    bdlc_lcd_codes = get_bdlc_codes(q)
        
    lcd_codes = cyclic_codes.union(quasi_cyclic_codes).union(bdlc_lcd_codes)
    return lcd_codes


def get_lcd_codes_q_excluding_quasi_cyclic(q:int) -> Set[LinearCodeRecord]:
    cyclic_codes = get_cyclic_codes(q)
    bdlc_lcd_codes = get_bdlc_codes(q)
        
    lcd_codes = cyclic_codes.union(bdlc_lcd_codes)
    return lcd_codes


# def get_random_lcd_code_q(q:int) -> LinearCodeRecord:
#     if q == 2:
#         return random.choice(list(lcd_codes_q2))
   
#     return random.choice(list(lcd_codes_q3))