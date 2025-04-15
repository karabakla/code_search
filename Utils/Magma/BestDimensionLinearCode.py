from traceback import print_exc
from typing import Dict, Tuple, Set
from time import sleep
from xmlrpc.client import Boolean

from Utils.Magma.Invoke_Online_Command import invoke_online_command
from Utils.Types import CyclicCodeRecord, LinearCodeRecord, QuasiCyclicCodeRecord
    
# class BDLC:
#     def __init__(self, verbose=False):
#         self.verbose = verbose
    
#     def __get_dimension_of_bdlc_from_magma__(self, q, n, d):
#         command = f"Dimension(BestDimensionLinearCode(FiniteField({q}),{n},{d}));"
#         response = invoke_online_command(command)
#         results = response.get_results()
#         if self.verbose:
#             print(results)
#         return results
    
#     def get_dimension_of_bdlc(self, q, n, d):        
#         bdlc_results = self.__get_dimension_of_bdlc_from_magma__(q, n, d)
#         if len(bdlc_results) == 0 or len(bdlc_results) > 1:
#             return bdlc_results, False
#         dimension = int(bdlc_results[0]), True
#         return dimension
    
# Combining multiple request into one magma call 

class BDLCRecord:
    def __init__(self, q:int, n:int, d:int):
        self.q:int = q
        self.n:int = n
        self.d:int = d

    def __eq__(self, other):
        return self.q == other.q and self.n == other.n and self.d == other.d

    def __hash__(self):
        return hash((self.q, self.n, self.d))

    def __str__(self):
        return f"BDLCRecord({self.q}, {self.n}, {self.d})"

    def __repr__(self):
        return self.__str__()

    def __lt__(self, other):
        return (self.q, self.n, self.d) < (other.q, other.n, other.d)
    

class BDLC:
    def __init__(self, maxTry=10, verbose=False):
        self._queue:Set[Tuple[int,BDLCRecord]] = set() # (unique_request_id, BDLCRecord)
        self._verbose = verbose
        self._unique_request_id = 0
    
    # Combine the command int to one
    def __invoke_requests__(self):
        command = "IsLCD := function(C) return C meet Dual(C) eq ZeroCode(BaseField(C), Length(C)); end function;"
        for id,request in self._queue:
            command = f"{command} \nprintf \"%o:[%o, %o, %o]_%o:%o\\n\",{id}, Length(BestDimensionLinearCode(FiniteField({request.q}),{request.n},{request.d})), Dimension(BestDimensionLinearCode(FiniteField({request.q}),{request.n},{request.d})), MinimumDistance(BestDimensionLinearCode(FiniteField({request.q}),{request.n},{request.d})), {request.q}, IsLCD(BestDimensionLinearCode(FiniteField({request.q}),{request.n},{request.d}));"
                
        response = invoke_online_command(command)
        results = response.get_results()
        if self._verbose:
            print(results)
        return results
    
    def __try_invoke_requests__(self, max_try=10, timeout=60000):
        try_count = 0
        while try_count < max_try:
            try:
                return self.__invoke_requests__()
            except:
                print_exc()
                sleep(10*try_count)
                pass
            
        return []
        
    def __get_next_unique_request_id__(self):
        self._unique_request_id += 1
        return self._unique_request_id
        
    def put_request(self, request:BDLCRecord) -> int:
        unique_request_id = self.__get_next_unique_request_id__()
        self._queue.add((unique_request_id, request))
        return unique_request_id

    def get_request_count(self):
        return len(self._queue)
    
    def __parse_response__(self, raw_response:str) -> Tuple[int, LinearCodeRecord] | None:
        # raw_response = "0:[60, 0, 50]_2:true"
        split_response = raw_response.split(":")
        
        if len(split_response) != 3:
            return None
        
        is_lcd = split_response[2].strip().lower() == "true"
        
        request_id = int(split_response[0])
        q = int(split_response[1].split("_")[1])
        
        split_response = split_response[1].split("_")[0] # type: ignore
        
        response = split_response.strip('[]').split(',') # type: ignore
        n = int(response[0])
        dim = int(response[1])
        min_distance = int(response[2])
        return request_id, LinearCodeRecord(q, n, dim, min_distance, is_lcd)
        
        
    
    def get_results(self) -> Dict[int, LinearCodeRecord]:
        if(len(self._queue) == 0):
            return {}
        bdlc_results_raw = self.__try_invoke_requests__()
        
        # Some unrecoverable error happened
        if(len(bdlc_results_raw) != len(self._queue)):
            raise Exception("Some unrecoverable error happened queue size mismatch")
        
       
        bdlc_results:Dict[int, LinearCodeRecord ] ={}
        
        for r in bdlc_results_raw:
            parsed_response = self.__parse_response__(r)
            if parsed_response is None:
                raise Exception("Some unrecoverable error happened parsing response")
            request_id, lc = parsed_response
            bdlc_results[request_id] = lc            
        
        self._queue.clear()
        return bdlc_results
        
# b = BDLC()

# b.put_request(BDLCRecord(2, 60, 50))
# b.put_request(LinearCodeRecord(3, 85, 0, 2))
# b.put_request(LinearCodeRecord(3, 85, 0, 8))
# b.put_request(LinearCodeRecord(3, 85, 0, 8))
# b.put_request(LinearCodeRecord(3, 85, 0, 8))
# b.put_request(LinearCodeRecord(3, 85, 0, 8))
# b.put_request(LinearCodeRecord(3, 85, 0, 4))

# print(b.get_results())