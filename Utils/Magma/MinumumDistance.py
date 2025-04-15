import traceback
from Utils.Magma.Invoke_Online_Command import invoke_online_command


class CyclicCodeMinDistance:
    @staticmethod
    def __get_min_distance__(q, n, gen_pol, verbose=False):
        command = f"P<x>:=PolynomialRing(FiniteField({q})); MinimumDistance(CyclicCode({n}, {gen_pol}));"
        response = invoke_online_command(command)
        results = response.get_results()
        if verbose:
            print(results)
        if len(results) == 0 or len(results) > 1:
            return -1
        return int(results[0])
    
    @staticmethod
    def get_min_distance(q, n, gen_pol) -> int | None:
        try:
            return CyclicCodeMinDistance.__get_min_distance__(q, n, gen_pol)
        except Exception as e:
            print(f"Error in CyclicCodeMinDistance.get_min_distance({q}, {n}, {e}")
            return None