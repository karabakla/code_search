
F2:=GF(2);

P<x> := PolynomialRing(F2);

//G := [1, 1, x^8 + x^6 + x^3 + x + 1, 0, x + 1,  x^8 + x^7 + x^5 + x^3];

// [[x + 1, 0, x^7 + x^6 + x^5 + x^2], [0, x + 1, x^5 + x^3 + x + 1]]
G := [x + 1, 0, x^7 + x^6 + x^5 + x^2, 0, x + 1, x^5 + x^3 + x + 1];

QC := QuasiCyclicCode(27, G, 2);

IsQuasiCyclic(QC,3);