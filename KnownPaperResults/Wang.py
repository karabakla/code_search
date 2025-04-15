
from typing import List


raw_table_0 ="""
_  9 10 11 12 13 14 15
38 14-15 14 13-14 12-14 11-12 10-12 10-12
39 15-16 14-15 13-14 12-14 11-13 11-12 10-12
40 15-16 14-16 14-15 13-14 12-14 12-13 11-12
"""

raw_table_1 ="""
_  6 7 8 9 10 11 12 13 14 15
41 19* 18* 17* 16* 15-16 14-16 14-15 13-14 12-14 11-13
42 20* 18 18* 17* 16* 14-16 14-16 13-14 13-14 12-14
43 20 19* 18 17-18 16-17 15-16 14-16 14-15 14* 13-14
44 20 19-20 18-19 18* 16-18 15-17 14-16 14-16 14-15 13-14
45 20 20* 18-20 18-19 16-18 16-18 15-16 14-16 14-16 14-15
46 21* 20 18-20 18-20 17-19 16-18 16-17 15-16 14-16 14-16
47 22* 20-21 19-20 18-20 18-20 17-18 16-18 15-17 14-16 14-16
48 22 21-22 20-21 18-20 18-20 17-19 17-18 16-18 15-17 14-16
49 23* 21-22 20-22 19-20 18-20 18-20 18-19 17-18 16-18 14-17
50 24* 22-23 20-22 19-21 18-20 18-20 18-20 17-19 17-18 14-18
"""

raw_table_2 ="""
_  16 17 18 19 20 21 22 23 24 25
41 10-12 10-12 10-12 10-11 10* 9-10 8-9 8* 7-8 6-8
42 11-13 10-12 10-12 10-12 10 9-10 8-10 8-9 8* 7-8
43 12-14 11-13 10-12 10-12 10-11 10* 8-10 8-10 8-9 7-8
44 13-14 11-14 11-12 10-12 10-12 10-11 8-10 8-10 8-10 8-9
45 14 12-14 12-13 10-12 10-12 10-12 9-11 8-10 8-10 8-10
46 14-15 12-14 12-14 11-13 10-12 10-12 10-12 9-11 8-10 8-10
47 14-16 12-15 12-14 11-14 11-13 10-12 10-12 9-12 9-11 8-10
48 14-16 12-16 12-15 12-14 12-14 11-13 10-12 10-12 10-12 9-12
49 14-16 13-16 12-15 12-14 12-14 11-14 10-13 10-12 10-12 9-12
50 14-17 13-16 13-16 12-15 12-14 12-14 11-14 10-13 10-12 10-12
"""

raw_table_3 ="""
_  26 27 28 29 30 31 32 33 34 35
41 6-7 6 6 5-6 4-5 4 4 4* 4* 3*
42 6-8 6-7 6 6* 5-6 4-5 4 4 4 3-4
43 7-8 6-8 6-7 6 6* 5-6 4-5 4 4 4*
44 8* 7-8 6-8 6-7 6 5-6 5-6 4-5 4 4
45 8-9 7-8 7-8 6-8 6-7 6* 6* 5-6 4-5 4
46 8-10 8-9 8* 7-8 6-8 6-7 6 5-6 5-6 4-5
47 8-10 8-10 8-9 7-8 7-8 6-8 6-7 6* 6* 5-6
48 8-10 8-10 8-10 8-9 8* 7-8 6-8 6-7 6 5-6
49 9-11 8-10 8-10 8-10 8 7-8 6-8 6-8 6-7 6*
50 10-12 9-10 8-10 8-10 8-9 8 7-8 6-8 6-8 6-7
"""

raw_table_4 ="""
_  36 37 38 39 40 41 42 43 44
42 3*
43 4* 3*
44 4 3-4 3*
45 4 4* 4* 3*
46 4 4 4 3-4 3*
47 4-5 4 4 4* 4* 3*
48 5-6 4-5 4 4 4 3-4 3*
49 6* 5-6 4-5 4 4 4* 4* 3*
50 6 5-6 5-6 4 4 4 4 3-4 3*
"""

class WangEntry:
    def __init__(self, n, k, dist):
        self.n = n
        self.k = k
        self.result = dist

    def __str__(self):
        return f"WangEntry(n={self.n}, k={self.k}, dist='{self.result}')"
    
    def __repr__(self):
        return self.__str__()
    
    
    def is_exactly_found(self) -> bool:
        return '-' not in self.result and self.result.strip() != ''
    
    def get_distance(self):
        res = self.result.strip('*')
        if '-' in res:
            return [int(k) for k in res.split('-')]
        
        return int(res)

    
wang_known_results:List[WangEntry] = []

def parse_table(raw_table:str) -> List[WangEntry]:
    lines = raw_table.strip().split("\n")
    header = [ int(k)  for k in lines[0].split()[1:]]
    data:List[WangEntry] = []
    for line in lines[1:]:
        parts = line.split()
        n = int(parts[0])
        for i, dist in enumerate(parts[1:]):
            k = header[i]
            data.append(WangEntry(n, k, dist))
    return data

wang_known_results.extend(parse_table(raw_table_0))
wang_known_results.extend(parse_table(raw_table_1))
wang_known_results.extend(parse_table(raw_table_2))
wang_known_results.extend(parse_table(raw_table_3))
wang_known_results.extend(parse_table(raw_table_4))

def Wang_Get_Largest_d(q, n, k) -> int | None:
    if q != 2:
        return None
    
    for entry in wang_known_results:
        if entry.n == n and entry.k == k and entry.is_exactly_found():
            return entry.get_distance() # type: ignore
    return None

# print(Wang_Get_Largest_d(2, 48, 20))