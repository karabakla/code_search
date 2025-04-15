\ Model Extended ILP
\ LP format - for model browsing. Use MPS format to capture full model detail.
\ Signature: 0x5e9fbc34582307f3
Maximize
  A[0] + A[1] + A[2]
Subject To
 R0: - 2 A[1] - 4 A[2] >= -4
 R1: - 2 A[0] + 6 A[2] >= -6
 R2: 2 A[1] - 4 A[2] >= -4
 R3: A[0] - A[1] + A[2] >= -1
 R4: 6 A[0] + 6 A[1] >= 0
 R5: 4 A[0] + 8 A[2] >= 0
 R6: 2 A[1] - 2 A[2] >= 0
 R7: A[0] + A[1] + A[2] >= 2
 R8: A[0] + A[1] + A[2] <= 8
Bounds
 A[0] <= 6
 A[1] <= 4
 A[2] <= 1
Generals
 A[0] A[1] A[2]
End
