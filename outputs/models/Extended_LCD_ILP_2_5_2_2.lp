\ Model Extended ILP
\ LP format - for model browsing. Use MPS format to capture full model detail.
\ Signature: 0xc4fdac2c34ca9cd
Maximize
  A[0] + A[1] + A[2] + A[3]
Subject To
 R0: A[0] - A[1] - 3 A[2] - 5 A[3] >= -5
 R1: - 2 A[0] - 2 A[1] + 2 A[2] + 10 A[3] >= -10
 R2: - 2 A[0] + 2 A[1] + 2 A[2] - 10 A[3] >= -10
 R3: A[0] + A[1] - 3 A[2] + 5 A[3] >= -5
 R4: A[0] - A[1] + A[2] - A[3] >= -1
 R5: 8 A[0] + 12 A[1] + 8 A[2] >= 0
 R6: 12 A[0] + 4 A[1] + 8 A[2] + 20 A[3] >= 0
 R7: 4 A[0] + 4 A[1] + 4 A[2] >= 0
 R8: 2 A[1] - 2 A[3] >= 0
 R9: A[0] >= 1
 R10: A[0] + A[1] + A[2] + A[3] >= 4
 R11: A[0] + A[1] + A[2] + A[3] <= 16
Bounds
 A[0] <= 10
 A[1] <= 10
 A[2] <= 5
 A[3] <= 1
Generals
 A[0] A[1] A[2] A[3]
End
