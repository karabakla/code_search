import csv


class StefkaEntry_nk:
    def __init__(self, n:int, k:int, result:str) -> None:
        self.n = n
        self.k = k
        self.result = result
    
    def __str__(self) -> str:
        return f"StefkaEntry [{self.n},{self.k}] = {self.result}"
    
    def __repr__(self) -> str:
        return str(self)
    
    def __dict__(self):
        return {
            'n': self.n,
            'k': self.k,
            'result': self.result
        }
    
    def is_explicity_found(self) -> bool:
        return self.result.endswith('*')
    
    def is_exactly_found(self) -> bool:
        return ',' not in self.result and self.result.strip() != ''
    
class StefkaEntry_nd:
    def __init__(self, n:int, d:int, result:int, explicity_found:bool) -> None:
        self.n = n
        self.d = d
        self.result = result
        self.explicity_found = explicity_found
    
    def __str__(self) -> str:
        return f"StefkaEntry [{self.n},{self.d}] = {self.result}"
    
    def __repr__(self) -> str:
        return str(self)
    
    def __dict__(self):
        return {
            'n': self.n,
            'd': self.d,
            'result': self.result,
            'explicity_found': self.explicity_found
        }
    
    def to_csv(self):
        return [self.n, self.d, self.result, self.explicity_found]

stefka_known_results_q2_nk = [
    [StefkaEntry_nk(16, 5, '6'), StefkaEntry_nk(16, 6, '6*'), StefkaEntry_nk(16, 7, '5'), StefkaEntry_nk(16, 8, '5*'), StefkaEntry_nk(16, 9, '4*'), StefkaEntry_nk(16, 10, '4*'), StefkaEntry_nk(16, 11, '3'), StefkaEntry_nk(16, 12, '2*'), StefkaEntry_nk(16, 13, '2*'), StefkaEntry_nk(16, 14, '2*'), StefkaEntry_nk(16, 15, '1'), StefkaEntry_nk(16, 16, '1'), StefkaEntry_nk(16, 17, ''), StefkaEntry_nk(16, 18, ''), StefkaEntry_nk(16, 19, ''), StefkaEntry_nk(16, 20, ''), StefkaEntry_nk(16, 21, ''), StefkaEntry_nk(16, 22, ''), StefkaEntry_nk(16, 23, ''), StefkaEntry_nk(16, 24, ''), StefkaEntry_nk(16, 25, ''), StefkaEntry_nk(16, 26, ''), StefkaEntry_nk(16, 27, ''), StefkaEntry_nk(16, 28, ''), StefkaEntry_nk(16, 29, ''), StefkaEntry_nk(16, 30, ''), StefkaEntry_nk(16, 31, ''), StefkaEntry_nk(16, 32, ''), ],
    [StefkaEntry_nk(17, 5, '7'), StefkaEntry_nk(17, 6, '6'), StefkaEntry_nk(17, 7, '6*'), StefkaEntry_nk(17, 8, '6*'), StefkaEntry_nk(17, 9, '5*'), StefkaEntry_nk(17, 10, '4*'), StefkaEntry_nk(17, 11, '3'), StefkaEntry_nk(17, 12, '3*'), StefkaEntry_nk(17, 13, '2*'), StefkaEntry_nk(17, 14, '2*'), StefkaEntry_nk(17, 15, '2*'), StefkaEntry_nk(17, 16, '2*'), StefkaEntry_nk(17, 17, '1'), StefkaEntry_nk(17, 18, ''), StefkaEntry_nk(17, 19, ''), StefkaEntry_nk(17, 20, ''), StefkaEntry_nk(17, 21, ''), StefkaEntry_nk(17, 22, ''), StefkaEntry_nk(17, 23, ''), StefkaEntry_nk(17, 24, ''), StefkaEntry_nk(17, 25, ''), StefkaEntry_nk(17, 26, ''), StefkaEntry_nk(17, 27, ''), StefkaEntry_nk(17, 28, ''), StefkaEntry_nk(17, 29, ''), StefkaEntry_nk(17, 30, ''), StefkaEntry_nk(17, 31, ''), StefkaEntry_nk(17, 32, ''), ],
    [StefkaEntry_nk(18, 5, '7'), StefkaEntry_nk(18, 6, '7'), StefkaEntry_nk(18, 7, '6'), StefkaEntry_nk(18, 8, '6*'), StefkaEntry_nk(18, 9, '5'), StefkaEntry_nk(18, 10, '4*'), StefkaEntry_nk(18, 11, '4*'), StefkaEntry_nk(18, 12, '4*'), StefkaEntry_nk(18, 13, '3*'), StefkaEntry_nk(18, 14, '2*'), StefkaEntry_nk(18, 15, '2*'), StefkaEntry_nk(18, 16, '2*'), StefkaEntry_nk(18, 17, '1'), StefkaEntry_nk(18, 18, ''), StefkaEntry_nk(18, 19, ''), StefkaEntry_nk(18, 20, ''), StefkaEntry_nk(18, 21, ''), StefkaEntry_nk(18, 22, ''), StefkaEntry_nk(18, 23, ''), StefkaEntry_nk(18, 24, ''), StefkaEntry_nk(18, 25, ''), StefkaEntry_nk(18, 26, ''), StefkaEntry_nk(18, 27, ''), StefkaEntry_nk(18, 28, ''), StefkaEntry_nk(18, 29, ''), StefkaEntry_nk(18, 30, ''), StefkaEntry_nk(18, 31, ''), StefkaEntry_nk(18, 32, ''), ],
    [StefkaEntry_nk(19, 5, '8*'), StefkaEntry_nk(19, 6, '8*'), StefkaEntry_nk(19, 7, '7'), StefkaEntry_nk(19, 8, '6'), StefkaEntry_nk(19, 9, '6*'), StefkaEntry_nk(19, 10, '5*'), StefkaEntry_nk(19, 11, '4*'), StefkaEntry_nk(19, 12, '4*'), StefkaEntry_nk(19, 13, '3'), StefkaEntry_nk(19, 14, '3*'), StefkaEntry_nk(19, 15, '2*'), StefkaEntry_nk(19, 16, '2*'), StefkaEntry_nk(19, 17, '2*'), StefkaEntry_nk(19, 18, ''), StefkaEntry_nk(19, 19, ''), StefkaEntry_nk(19, 20, ''), StefkaEntry_nk(19, 21, ''), StefkaEntry_nk(19, 22, ''), StefkaEntry_nk(19, 23, ''), StefkaEntry_nk(19, 24, ''), StefkaEntry_nk(19, 25, ''), StefkaEntry_nk(19, 26, ''), StefkaEntry_nk(19, 27, ''), StefkaEntry_nk(19, 28, ''), StefkaEntry_nk(19, 29, ''), StefkaEntry_nk(19, 30, ''), StefkaEntry_nk(19, 31, ''), StefkaEntry_nk(19, 32, ''), ],
    [StefkaEntry_nk(20, 5, '9*'), StefkaEntry_nk(20, 6, '8*'), StefkaEntry_nk(20, 7, '7'), StefkaEntry_nk(20, 8, '6'), StefkaEntry_nk(20, 9, '6'), StefkaEntry_nk(20, 10, '6*'), StefkaEntry_nk(20, 11, '5*'), StefkaEntry_nk(20, 12, '4*'), StefkaEntry_nk(20, 13, '4*'), StefkaEntry_nk(20, 14, '4*'), StefkaEntry_nk(20, 15, '3*'), StefkaEntry_nk(20, 16, '2*'), StefkaEntry_nk(20, 17, '2*'), StefkaEntry_nk(20, 18, ''), StefkaEntry_nk(20, 19, ''), StefkaEntry_nk(20, 20, ''), StefkaEntry_nk(20, 21, ''), StefkaEntry_nk(20, 22, ''), StefkaEntry_nk(20, 23, ''), StefkaEntry_nk(20, 24, ''), StefkaEntry_nk(20, 25, ''), StefkaEntry_nk(20, 26, ''), StefkaEntry_nk(20, 27, ''), StefkaEntry_nk(20, 28, ''), StefkaEntry_nk(20, 29, ''), StefkaEntry_nk(20, 30, ''), StefkaEntry_nk(20, 31, ''), StefkaEntry_nk(20, 32, ''), ],
    [StefkaEntry_nk(21, 5, '9'), StefkaEntry_nk(21, 6, '8*'), StefkaEntry_nk(21, 7, '8*'), StefkaEntry_nk(21, 8, '7'), StefkaEntry_nk(21, 9, '6'), StefkaEntry_nk(21, 10, '6'), StefkaEntry_nk(21, 11, '5'), StefkaEntry_nk(21, 12, '5*'), StefkaEntry_nk(21, 13, '4*'), StefkaEntry_nk(21, 14, '4*'), StefkaEntry_nk(21, 15, '3'), StefkaEntry_nk(21, 16, '3*'), StefkaEntry_nk(21, 17, '2*'), StefkaEntry_nk(21, 18, ''), StefkaEntry_nk(21, 19, ''), StefkaEntry_nk(21, 20, ''), StefkaEntry_nk(21, 21, ''), StefkaEntry_nk(21, 22, ''), StefkaEntry_nk(21, 23, ''), StefkaEntry_nk(21, 24, ''), StefkaEntry_nk(21, 25, ''), StefkaEntry_nk(21, 26, ''), StefkaEntry_nk(21, 27, ''), StefkaEntry_nk(21, 28, ''), StefkaEntry_nk(21, 29, ''), StefkaEntry_nk(21, 30, ''), StefkaEntry_nk(21, 31, ''), StefkaEntry_nk(21, 32, ''), ],
    [StefkaEntry_nk(22, 5, '10*'), StefkaEntry_nk(22, 6, '9*'), StefkaEntry_nk(22, 7, '8*'), StefkaEntry_nk(22, 8, '8*'), StefkaEntry_nk(22, 9, '7'), StefkaEntry_nk(22, 10, '6'), StefkaEntry_nk(22, 11, '6'), StefkaEntry_nk(22, 12, '6*'), StefkaEntry_nk(22, 13, '5*'), StefkaEntry_nk(22, 14, '4*'), StefkaEntry_nk(22, 15, '4*'), StefkaEntry_nk(22, 16, '4*'), StefkaEntry_nk(22, 17, '3*'), StefkaEntry_nk(22, 18, ''), StefkaEntry_nk(22, 19, ''), StefkaEntry_nk(22, 20, ''), StefkaEntry_nk(22, 21, ''), StefkaEntry_nk(22, 22, ''), StefkaEntry_nk(22, 23, ''), StefkaEntry_nk(22, 24, ''), StefkaEntry_nk(22, 25, ''), StefkaEntry_nk(22, 26, ''), StefkaEntry_nk(22, 27, ''), StefkaEntry_nk(22, 28, ''), StefkaEntry_nk(22, 29, ''), StefkaEntry_nk(22, 30, ''), StefkaEntry_nk(22, 31, ''), StefkaEntry_nk(22, 32, ''), ],
    [StefkaEntry_nk(23, 5, '10'), StefkaEntry_nk(23, 6, '10*'), StefkaEntry_nk(23, 7, '9*'), StefkaEntry_nk(23, 8, '8*'), StefkaEntry_nk(23, 9, '7'), StefkaEntry_nk(23, 10, '7'), StefkaEntry_nk(23, 11, '6'), StefkaEntry_nk(23, 12, '6'), StefkaEntry_nk(23, 13, '5'), StefkaEntry_nk(23, 14, '4'), StefkaEntry_nk(23, 15, '4*'), StefkaEntry_nk(23, 16, '4*'), StefkaEntry_nk(23, 17, '3'), StefkaEntry_nk(23, 18, '3*'), StefkaEntry_nk(23, 19, '2*'), StefkaEntry_nk(23, 20, '2*'), StefkaEntry_nk(23, 21, '2*'), StefkaEntry_nk(23, 22, '2*'), StefkaEntry_nk(23, 23, '1'), StefkaEntry_nk(23, 24, ''), StefkaEntry_nk(23, 25, ''), StefkaEntry_nk(23, 26, ''), StefkaEntry_nk(23, 27, ''), StefkaEntry_nk(23, 28, ''), StefkaEntry_nk(23, 29, ''), StefkaEntry_nk(23, 30, ''), StefkaEntry_nk(23, 31, ''), StefkaEntry_nk(23, 32, ''), ],
    [StefkaEntry_nk(24, 5, '11'), StefkaEntry_nk(24, 6, '10*'), StefkaEntry_nk(24, 7, '9'), StefkaEntry_nk(24, 8, '8*'), StefkaEntry_nk(24, 9, '8*'), StefkaEntry_nk(24, 10, '8*'), StefkaEntry_nk(24, 11, '7'), StefkaEntry_nk(24, 12, '6'), StefkaEntry_nk(24, 13, '6*'), StefkaEntry_nk(24, 14, '5'), StefkaEntry_nk(24, 15, '4*'), StefkaEntry_nk(24, 16, '4*'), StefkaEntry_nk(24, 17, '4*'), StefkaEntry_nk(24, 18, '4*'), StefkaEntry_nk(24, 19, '3*'), StefkaEntry_nk(24, 20, '2*'), StefkaEntry_nk(24, 21, '2*'), StefkaEntry_nk(24, 22, '2*'), StefkaEntry_nk(24, 23, '1'), StefkaEntry_nk(24, 24, '1'), StefkaEntry_nk(24, 25, ''), StefkaEntry_nk(24, 26, ''), StefkaEntry_nk(24, 27, ''), StefkaEntry_nk(24, 28, ''), StefkaEntry_nk(24, 29, ''), StefkaEntry_nk(24, 30, ''), StefkaEntry_nk(24, 31, ''), StefkaEntry_nk(24, 32, ''), ],
    [StefkaEntry_nk(25, 5, '11'), StefkaEntry_nk(25, 6, '10'), StefkaEntry_nk(25, 7, '10*'), StefkaEntry_nk(25, 8, '9*'), StefkaEntry_nk(25, 9, '8*'), StefkaEntry_nk(25, 10, '8*'), StefkaEntry_nk(25, 11, '7'), StefkaEntry_nk(25, 12, '7'), StefkaEntry_nk(25, 13, '6*'), StefkaEntry_nk(25, 14, '6*'), StefkaEntry_nk(25, 15, '5*'), StefkaEntry_nk(25, 16, '4*'), StefkaEntry_nk(25, 17, '4*'), StefkaEntry_nk(25, 18, '4*'), StefkaEntry_nk(25, 19, '3'), StefkaEntry_nk(25, 20, '3*'), StefkaEntry_nk(25, 21, '2*'), StefkaEntry_nk(25, 22, '2*'), StefkaEntry_nk(25, 23, '2*'), StefkaEntry_nk(25, 24, '2*'), StefkaEntry_nk(25, 25, '1'), StefkaEntry_nk(25, 26, ''), StefkaEntry_nk(25, 27, ''), StefkaEntry_nk(25, 28, ''), StefkaEntry_nk(25, 29, ''), StefkaEntry_nk(25, 30, ''), StefkaEntry_nk(25, 31, ''), StefkaEntry_nk(25, 32, ''), ],
    [StefkaEntry_nk(26, 5, '12*'), StefkaEntry_nk(26, 6, '11'), StefkaEntry_nk(26, 7, '10'), StefkaEntry_nk(26, 8, '10*'), StefkaEntry_nk(26, 9, '9*'), StefkaEntry_nk(26, 10, '8*'), StefkaEntry_nk(26, 11, '8*'), StefkaEntry_nk(26, 12, '8*'), StefkaEntry_nk(26, 13, '7*'), StefkaEntry_nk(26, 14, '6*'), StefkaEntry_nk(26, 15, '5,6'), StefkaEntry_nk(26, 16, '5*'), StefkaEntry_nk(26, 17, '4*'), StefkaEntry_nk(26, 18, '4*'), StefkaEntry_nk(26, 19, '4*'), StefkaEntry_nk(26, 20, '4*'), StefkaEntry_nk(26, 21, '3*'), StefkaEntry_nk(26, 22, '2*'), StefkaEntry_nk(26, 23, '2*'), StefkaEntry_nk(26, 24, '2*'), StefkaEntry_nk(26, 25, '1'), StefkaEntry_nk(26, 26, '1'), StefkaEntry_nk(26, 27, ''), StefkaEntry_nk(26, 28, ''), StefkaEntry_nk(26, 29, ''), StefkaEntry_nk(26, 30, ''), StefkaEntry_nk(26, 31, ''), StefkaEntry_nk(26, 32, ''), ],
    [StefkaEntry_nk(27, 5, '12'), StefkaEntry_nk(27, 6, '12*'), StefkaEntry_nk(27, 7, '11'), StefkaEntry_nk(27, 8, '10*'), StefkaEntry_nk(27, 9, '9'), StefkaEntry_nk(27, 10, '9*'), StefkaEntry_nk(27, 11, '8*'), StefkaEntry_nk(27, 12, '8*'), StefkaEntry_nk(27, 13, '7'), StefkaEntry_nk(27, 14, '6'), StefkaEntry_nk(27, 15, '6*'), StefkaEntry_nk(27, 16, '6*'), StefkaEntry_nk(27, 17, '5*'), StefkaEntry_nk(27, 18, '4*'), StefkaEntry_nk(27, 19, '4*'), StefkaEntry_nk(27, 20, '4*'), StefkaEntry_nk(27, 21, '3'), StefkaEntry_nk(27, 22, '2'), StefkaEntry_nk(27, 23, '2*'), StefkaEntry_nk(27, 24, '2*'), StefkaEntry_nk(27, 25, '2*'), StefkaEntry_nk(27, 26, '2*'), StefkaEntry_nk(27, 27, '1'), StefkaEntry_nk(27, 28, ''), StefkaEntry_nk(27, 29, ''), StefkaEntry_nk(27, 30, ''), StefkaEntry_nk(27, 31, ''), StefkaEntry_nk(27, 32, ''), ],
    [StefkaEntry_nk(28, 5, '13'), StefkaEntry_nk(28, 6, '12*'), StefkaEntry_nk(28, 7, '11'), StefkaEntry_nk(28, 8, '10'), StefkaEntry_nk(28, 9, '10*'), StefkaEntry_nk(28, 10, '10*'), StefkaEntry_nk(28, 11, '8*'), StefkaEntry_nk(28, 12, '8*'), StefkaEntry_nk(28, 13, '8*'), StefkaEntry_nk(28, 14, '7'), StefkaEntry_nk(28, 15, '6*'), StefkaEntry_nk(28, 16, '6*'), StefkaEntry_nk(28, 17, '5,6'), StefkaEntry_nk(28, 18, '5*'), StefkaEntry_nk(28, 19, '4*'), StefkaEntry_nk(28, 20, '4*'), StefkaEntry_nk(28, 21, '4*'), StefkaEntry_nk(28, 22, '3'), StefkaEntry_nk(28, 23, '2'), StefkaEntry_nk(28, 24, '2*'), StefkaEntry_nk(28, 25, '2*'), StefkaEntry_nk(28, 26, '2*'), StefkaEntry_nk(28, 27, '1'), StefkaEntry_nk(28, 28, '1'), StefkaEntry_nk(28, 29, ''), StefkaEntry_nk(28, 30, ''), StefkaEntry_nk(28, 31, ''), StefkaEntry_nk(28, 32, ''), ],
    [StefkaEntry_nk(29, 5, '13'), StefkaEntry_nk(29, 6, '12'), StefkaEntry_nk(29, 7, '12*'), StefkaEntry_nk(29, 8, '11'), StefkaEntry_nk(29, 9, '10'), StefkaEntry_nk(29, 10, '10*'), StefkaEntry_nk(29, 11, '8,9'), StefkaEntry_nk(29, 12, '8*'), StefkaEntry_nk(29, 13, '8*'), StefkaEntry_nk(29, 14, '8*'), StefkaEntry_nk(29, 15, '6'), StefkaEntry_nk(29, 16, '6*'), StefkaEntry_nk(29, 17, '6*'), StefkaEntry_nk(29, 18, '6*'), StefkaEntry_nk(29, 19, '5*'), StefkaEntry_nk(29, 20, '4*'), StefkaEntry_nk(29, 21, '4*'), StefkaEntry_nk(29, 22, '4*'), StefkaEntry_nk(29, 23, '3'), StefkaEntry_nk(29, 24, '2'), StefkaEntry_nk(29, 25, '2*'), StefkaEntry_nk(29, 26, '2*'), StefkaEntry_nk(29, 27, '2*'), StefkaEntry_nk(29, 28, '2*'), StefkaEntry_nk(29, 29, '1'), StefkaEntry_nk(29, 30, ''), StefkaEntry_nk(29, 31, ''), StefkaEntry_nk(29, 32, ''), ],
    [StefkaEntry_nk(30, 5, '14'), StefkaEntry_nk(30, 6, '13'), StefkaEntry_nk(30, 7, '12*'), StefkaEntry_nk(30, 8, '12*'), StefkaEntry_nk(30, 9, '11'), StefkaEntry_nk(30, 10, '10'), StefkaEntry_nk(30, 11, '8,10'), StefkaEntry_nk(30, 12, '8,9'), StefkaEntry_nk(30, 13, '8*'), StefkaEntry_nk(30, 14, '8*'), StefkaEntry_nk(30, 15, '6,7'), StefkaEntry_nk(30, 16, '6'), StefkaEntry_nk(30, 17, '6*'), StefkaEntry_nk(30, 18, '6*'), StefkaEntry_nk(30, 19, '5,6'), StefkaEntry_nk(30, 20, '5*'), StefkaEntry_nk(30, 21, '4*'), StefkaEntry_nk(30, 22, '4*'), StefkaEntry_nk(30, 23, '4*'), StefkaEntry_nk(30, 24, '3'), StefkaEntry_nk(30, 25, '2'), StefkaEntry_nk(30, 26, '2*'), StefkaEntry_nk(30, 27, '2*'), StefkaEntry_nk(30, 28, '2*'), StefkaEntry_nk(30, 29, '1'), StefkaEntry_nk(30, 30, '1'), StefkaEntry_nk(30, 31, ''), StefkaEntry_nk(30, 32, ''), ],
    [StefkaEntry_nk(31, 5, '14'), StefkaEntry_nk(31, 6, '14'), StefkaEntry_nk(31, 7, '13*'), StefkaEntry_nk(31, 8, '12*'), StefkaEntry_nk(31, 9, '11'), StefkaEntry_nk(31, 10, '10'), StefkaEntry_nk(31, 11, '9,10'), StefkaEntry_nk(31, 12, '8,10'), StefkaEntry_nk(31, 13, '8,9'), StefkaEntry_nk(31, 14, '8*'), StefkaEntry_nk(31, 15, '6,8'), StefkaEntry_nk(31, 16, '6,7'), StefkaEntry_nk(31, 17, '6'), StefkaEntry_nk(31, 18, '6*'), StefkaEntry_nk(31, 19, '6*'), StefkaEntry_nk(31, 20, '6*'), StefkaEntry_nk(31, 21, '4,5'), StefkaEntry_nk(31, 22, '4*'), StefkaEntry_nk(31, 23, '4*'), StefkaEntry_nk(31, 24, '4*'), StefkaEntry_nk(31, 25, '3'), StefkaEntry_nk(31, 26, '2'), StefkaEntry_nk(31, 27, '2*'), StefkaEntry_nk(31, 28, '2*'), StefkaEntry_nk(31, 29, '2*'), StefkaEntry_nk(31, 30, '2*'), StefkaEntry_nk(31, 31, '1'), StefkaEntry_nk(31, 32, ''), ],
    [StefkaEntry_nk(32, 5, '15'), StefkaEntry_nk(32, 6, '14'), StefkaEntry_nk(32, 7, '13'), StefkaEntry_nk(32, 8, '12'), StefkaEntry_nk(32, 9, '12*'), StefkaEntry_nk(32, 10, '11'), StefkaEntry_nk(32, 11, '10'), StefkaEntry_nk(32, 12, '9,10'), StefkaEntry_nk(32, 13, '8,10'), StefkaEntry_nk(32, 14, '8,9'), StefkaEntry_nk(32, 15, '6,8'), StefkaEntry_nk(32, 16, '6,8'), StefkaEntry_nk(32, 17, '6,7'), StefkaEntry_nk(32, 18, '6'), StefkaEntry_nk(32, 19, '6*'), StefkaEntry_nk(32, 20, '6*'), StefkaEntry_nk(32, 21, '4,6'), StefkaEntry_nk(32, 22, '4,5'), StefkaEntry_nk(32, 23, '4*'), StefkaEntry_nk(32, 24, '4*'), StefkaEntry_nk(32, 25, '3,4'), StefkaEntry_nk(32, 26, '3'), StefkaEntry_nk(32, 27, '2*'), StefkaEntry_nk(32, 28, '2*'), StefkaEntry_nk(32, 29, '2*'), StefkaEntry_nk(32, 30, '2*'), StefkaEntry_nk(32, 31, '1'), StefkaEntry_nk(32, 32, '1'), ],
    [StefkaEntry_nk(33, 5, '15'), StefkaEntry_nk(33, 6, '14'), StefkaEntry_nk(33, 7, '14*'), StefkaEntry_nk(33, 8, '13'), StefkaEntry_nk(33, 9, '12*'), StefkaEntry_nk(33, 10, '12*'), StefkaEntry_nk(33, 11, '10,11'), StefkaEntry_nk(33, 12, '10'), StefkaEntry_nk(33, 13, '9,10'), StefkaEntry_nk(33, 14, '8,10'), StefkaEntry_nk(33, 15, '7,9'), StefkaEntry_nk(33, 16, '6,8'), StefkaEntry_nk(33, 17, '6,8'), StefkaEntry_nk(33, 18, '6,7'), StefkaEntry_nk(33, 19, '6'), StefkaEntry_nk(33, 20, '6*'), StefkaEntry_nk(33, 21, '4,6'), StefkaEntry_nk(33, 22, '4,6'), StefkaEntry_nk(33, 23, '4,5'), StefkaEntry_nk(33, 24, '4*'), StefkaEntry_nk(33, 25, '4*'), StefkaEntry_nk(33, 26, '4*'), StefkaEntry_nk(33, 27, '3*'), StefkaEntry_nk(33, 28, '2*'), StefkaEntry_nk(33, 29, '2*'), StefkaEntry_nk(33, 30, '2*'), StefkaEntry_nk(33, 31, '2*'), StefkaEntry_nk(33, 32, '2*'), ],
    [StefkaEntry_nk(34, 5, '16*'), StefkaEntry_nk(34, 6, '15'), StefkaEntry_nk(34, 7, '14'), StefkaEntry_nk(34, 8, '14*'), StefkaEntry_nk(34, 9, '12,13'), StefkaEntry_nk(34, 10, '12*'), StefkaEntry_nk(34, 11, '11,12'), StefkaEntry_nk(34, 12, '11'), StefkaEntry_nk(34, 13, '9,10'), StefkaEntry_nk(34, 14, '9,10'), StefkaEntry_nk(34, 15, '8,10'), StefkaEntry_nk(34, 16, '7,9'), StefkaEntry_nk(34, 17, '6,8'), StefkaEntry_nk(34, 18, '6,8'), StefkaEntry_nk(34, 19, '6,7'), StefkaEntry_nk(34, 20, '6'), StefkaEntry_nk(34, 21, '4,6'), StefkaEntry_nk(34, 22, '4,6'), StefkaEntry_nk(34, 23, '4,6'), StefkaEntry_nk(34, 24, '4*'), StefkaEntry_nk(34, 25, '4*'), StefkaEntry_nk(34, 26, '4*'), StefkaEntry_nk(34, 27, '3,4'), StefkaEntry_nk(34, 28, '3*'), StefkaEntry_nk(34, 29, '2*'), StefkaEntry_nk(34, 30, '2*'), StefkaEntry_nk(34, 31, '2*'), StefkaEntry_nk(34, 32, '2*'), ],
    [StefkaEntry_nk(35, 5, '16*'), StefkaEntry_nk(35, 6, '16*'), StefkaEntry_nk(35, 7, '15'), StefkaEntry_nk(35, 8, '14'), StefkaEntry_nk(35, 9, '12,14'), StefkaEntry_nk(35, 10, '12,13'), StefkaEntry_nk(35, 11, '12*'), StefkaEntry_nk(35, 12, '12*'), StefkaEntry_nk(35, 13, '10,11'), StefkaEntry_nk(35, 14, '10*'), StefkaEntry_nk(35, 15, '9,10'), StefkaEntry_nk(35, 16, '8,10'), StefkaEntry_nk(35, 17, '6,8'), StefkaEntry_nk(35, 18, '6,8'), StefkaEntry_nk(35, 19, '6,8'), StefkaEntry_nk(35, 20, '6,7'), StefkaEntry_nk(35, 21, '4,6'), StefkaEntry_nk(35, 22, '4,6'), StefkaEntry_nk(35, 23, '4,6'), StefkaEntry_nk(35, 24, '4,5'), StefkaEntry_nk(35, 25, '4*'), StefkaEntry_nk(35, 26, '4*'), StefkaEntry_nk(35, 27, '4*'), StefkaEntry_nk(35, 28, '4*'), StefkaEntry_nk(35, 29, '3*'), StefkaEntry_nk(35, 30, '2*'), StefkaEntry_nk(35, 31, '2*'), StefkaEntry_nk(35, 32, '2*'), ],
    [StefkaEntry_nk(36, 5, '17*'), StefkaEntry_nk(36, 6, '16*'), StefkaEntry_nk(36, 7, '15'), StefkaEntry_nk(36, 8, '14'), StefkaEntry_nk(36, 9, '12,14'), StefkaEntry_nk(36, 10, '12,14'), StefkaEntry_nk(36, 11, '12,13'), StefkaEntry_nk(36, 12, '12*'), StefkaEntry_nk(36, 13, '10,12'), StefkaEntry_nk(36, 14, '10,11'), StefkaEntry_nk(36, 15, '9,10'), StefkaEntry_nk(36, 16, '9,10'), StefkaEntry_nk(36, 17, '6,9'), StefkaEntry_nk(36, 18, '6,8'), StefkaEntry_nk(36, 19, '6,8'), StefkaEntry_nk(36, 20, '6,8'), StefkaEntry_nk(36, 21, '4,7'), StefkaEntry_nk(36, 22, '4,6'), StefkaEntry_nk(36, 23, '4,6'), StefkaEntry_nk(36, 24, '4,6'), StefkaEntry_nk(36, 25, '4,5'), StefkaEntry_nk(36, 26, '4*'), StefkaEntry_nk(36, 27, '4*'), StefkaEntry_nk(36, 28, '4*'), StefkaEntry_nk(36, 29, '3,4'), StefkaEntry_nk(36, 30, '3*'), StefkaEntry_nk(36, 31, '2*'), StefkaEntry_nk(36, 32, '2*'), ],
    [StefkaEntry_nk(37, 5, '17'), StefkaEntry_nk(37, 6, '16'), StefkaEntry_nk(37, 7, '16*'), StefkaEntry_nk(37, 8, '15'), StefkaEntry_nk(37, 9, '12,14'), StefkaEntry_nk(37, 10, '12,14'), StefkaEntry_nk(37, 11, '12,14'), StefkaEntry_nk(37, 12, '12,13'), StefkaEntry_nk(37, 13, '10,12'), StefkaEntry_nk(37, 14, '10,12'), StefkaEntry_nk(37, 15, '10,11'), StefkaEntry_nk(37, 16, '10*'), StefkaEntry_nk(37, 17, '6,10'), StefkaEntry_nk(37, 18, '6,9'), StefkaEntry_nk(37, 19, '6,8'), StefkaEntry_nk(37, 20, '6,8'), StefkaEntry_nk(37, 21, '4,8'), StefkaEntry_nk(37, 22, '4,7'), StefkaEntry_nk(37, 23, '4,6'), StefkaEntry_nk(37, 24, '4,6'), StefkaEntry_nk(37, 25, '4,6'), StefkaEntry_nk(37, 26, '4,5'), StefkaEntry_nk(37, 27, '4*'), StefkaEntry_nk(37, 28, '4*'), StefkaEntry_nk(37, 29, '4*'), StefkaEntry_nk(37, 30, '4*'), StefkaEntry_nk(37, 31, '3*'), StefkaEntry_nk(37, 32, '2*'), ],
    [StefkaEntry_nk(38, 5, '18*'), StefkaEntry_nk(38, 6, '17'), StefkaEntry_nk(38, 7, '16*'), StefkaEntry_nk(38, 8, '16*'), StefkaEntry_nk(38, 9, '12,15'), StefkaEntry_nk(38, 10, '12,14'), StefkaEntry_nk(38, 11, '12,14'), StefkaEntry_nk(38, 12, '12,14'), StefkaEntry_nk(38, 13, '10,12'), StefkaEntry_nk(38, 14, '10,12'), StefkaEntry_nk(38, 15, '10,12'), StefkaEntry_nk(38, 16, '10,11'), StefkaEntry_nk(38, 17, '6,10'), StefkaEntry_nk(38, 18, '6,10'), StefkaEntry_nk(38, 19, '6,9'), StefkaEntry_nk(38, 20, '6,8'), StefkaEntry_nk(38, 21, '4,8'), StefkaEntry_nk(38, 22, '4,8'), StefkaEntry_nk(38, 23, '4,7'), StefkaEntry_nk(38, 24, '4,6'), StefkaEntry_nk(38, 25, '4,6'), StefkaEntry_nk(38, 26, '4,6'), StefkaEntry_nk(38, 27, '4,5'), StefkaEntry_nk(38, 28, '4*'), StefkaEntry_nk(38, 29, '4*'), StefkaEntry_nk(38, 30, '4*'), StefkaEntry_nk(38, 31, '3,4'), StefkaEntry_nk(38, 32, '3*'), ],
    [StefkaEntry_nk(39, 5, '18'), StefkaEntry_nk(39, 6, '18*'), StefkaEntry_nk(39, 7, '17*'), StefkaEntry_nk(39, 8, '16*'), StefkaEntry_nk(39, 9, '12,16'), StefkaEntry_nk(39, 10, '12,15'), StefkaEntry_nk(39, 11, '12,14'), StefkaEntry_nk(39, 12, '12,14'), StefkaEntry_nk(39, 13, '10,13'), StefkaEntry_nk(39, 14, '10,12'), StefkaEntry_nk(39, 15, '10,12'), StefkaEntry_nk(39, 16, '10,12'), StefkaEntry_nk(39, 17, '6,11'), StefkaEntry_nk(39, 18, '6,10'), StefkaEntry_nk(39, 19, '6,10'), StefkaEntry_nk(39, 20, '6,9'), StefkaEntry_nk(39, 21, '4,8'), StefkaEntry_nk(39, 22, '4,8'), StefkaEntry_nk(39, 23, '4,8'), StefkaEntry_nk(39, 24, '4,7'), StefkaEntry_nk(39, 25, '4,6'), StefkaEntry_nk(39, 26, '4,6'), StefkaEntry_nk(39, 27, '4,6'), StefkaEntry_nk(39, 28, '4,5'), StefkaEntry_nk(39, 29, '4*'), StefkaEntry_nk(39, 30, '4*'), StefkaEntry_nk(39, 31, '4*'), StefkaEntry_nk(39, 32, '4*'), ],
    [StefkaEntry_nk(40, 5, '19'), StefkaEntry_nk(40, 6, '18*'), StefkaEntry_nk(40, 7, '17'), StefkaEntry_nk(40, 8, '16*'), StefkaEntry_nk(40, 9, '12,16'), StefkaEntry_nk(40, 10, '12,16'), StefkaEntry_nk(40, 11, '12,15'), StefkaEntry_nk(40, 12, '12,14'), StefkaEntry_nk(40, 13, '10,14'), StefkaEntry_nk(40, 14, '10,13'), StefkaEntry_nk(40, 15, '10,12'), StefkaEntry_nk(40, 16, '10,12'), StefkaEntry_nk(40, 17, '6,12'), StefkaEntry_nk(40, 18, '6,11'), StefkaEntry_nk(40, 19, '6,10'), StefkaEntry_nk(40, 20, '6,10'), StefkaEntry_nk(40, 21, '4,9'), StefkaEntry_nk(40, 22, '4,8'), StefkaEntry_nk(40, 23, '4,8'), StefkaEntry_nk(40, 24, '4,8'), StefkaEntry_nk(40, 25, '4,7'), StefkaEntry_nk(40, 26, '4,6'), StefkaEntry_nk(40, 27, '4,6'), StefkaEntry_nk(40, 28, '4,6'), StefkaEntry_nk(40, 29, '4,5'), StefkaEntry_nk(40, 30, '4*'), StefkaEntry_nk(40, 31, '4*'), StefkaEntry_nk(40, 32, '4*'), ],
]    

def Stefka_Get_Largest_d(q, n, k) -> int | list[int]:
    if q > 2:
        return None
    
    for row in stefka_known_results_q2_nk:
        for entry in row:
            if entry.n == n and entry.k == k:
                if entry.is_exactly_found():
                    return int(entry.result.replace('*', '').strip())
                # if entry.is_exactly_found():
                #     return int(entry.result.replace('*', '').strip())
                # else:
                #     return [ int(r) for r in entry.result.split(',')]
    return None

# stefka_known_results_q2_nd = []

# for row_nk in stefka_known_results_q2_nk:
#     row_nd = []
#     for entry in row_nk:
#         if not entry.is_exactly_found():
#             continue
#         explicity_found = entry.is_explicity_found()
#         result = entry.result
#         if explicity_found:
#             result = result.replace('*', '').strip()
#         if result == '':
#             continue
            
#         row_nd.append(StefkaEntry_nd(entry.n, int(result), entry.k , explicity_found))
#     stefka_known_results_q2_nd.append(row_nd)
    
# def is_stefka_known_result_q2_nd(n, k):
#     return any(entry.n == n and entry.k == k for row in stefka_known_results_q2_nd for entry in row)

# def get_stefka_known_result_q2_nd(n, d):
#     try:
#         return max(entry.result for row in stefka_known_results_q2_nd for entry in row  if entry.n == n and entry.d == d)
#     except:
#         return None
