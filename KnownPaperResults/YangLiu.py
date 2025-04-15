# Yang Liu et. al. On the minimum distances of binary optimal LCD codes with dimension 5

def YangLiu_Get_Largest_q2_k5_d(n:int) -> int | None:
    if n <5:
        return None
                      #t:   0    1   2   3   4   5   6
    d_l_differences = [ -2, -1, -1, 0, 0, 1, 1, 
                        2, 2, 3, 3, 4, 4, 5,
                        5, 6, 6, 7, 7, 8, 9,
                        9, 10, 10, 11, 11, 12, 12,
                        13, 13, 14
                    ]
    
    s = n//31
    t = n%31
    
    return 16*s + d_l_differences[t]
    
    
#print(YangLiu_Get_Largest_q2_k5_d(9)) # 14

def YangLiu_Get_Largest_d(q:int, n:int, k:int) -> int | None:
    if q == 2 and k == 5:
            return YangLiu_Get_Largest_q2_k5_d(n)
    return None

