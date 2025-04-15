intrinsic IsZeroCode(C::CodeLinFld) -> BoolElt
{Returns true if the code C is the zero code.}
    return C eq ZeroCode(BaseField(C), Length(C));
end intrinsic;

intrinsic HasIntersection(C1::CodeLinFld, C2::CodeLinFld) -> BoolElt
{Returns true if the codes C1 and C2 have a non-trivial intersection.}
    return C1 meet C2 ne ZeroCode(BaseField(C1), Length(C1));
    
end intrinsic;

intrinsic IsLCDCode(C::CodeLinFld) -> BoolElt
{Returns true if the code C is LCD.}
    return HasIntersection(C, Dual(C)) eq false;
end intrinsic;

intrinsic IsHermDual(C::CodeLinFld) -> BoolElt
{Returns true if the code C is Herm dual.}
    return HasIntersection(C , HermDual(C)) eq false;
end intrinsic;

intrinsic GenerateRandomLCDCode(K::FldFin, n::RngIntElt, k::RngIntElt, maxTry::RngIntElt) -> CodeLinFld
{Generates a random LCD code of length n and dimension k over the field K.}
    for i := 1 to maxTry do
        C := RandomLinearCode(K, n, k);
        if IsLCDCode(C) then
            return C;
        end if;
    end for;

    return ZeroCode(K, n);    
end intrinsic;

intrinsic GenerateRandomHermDualCode(K::FldFin, n::RngIntElt, k::RngIntElt, maxTry::RngIntElt) -> CodeLinFld
{Generates a random Herm dual code of length n and dimension k over the field K.}
    for i := 1 to maxTry do
        C := RandomLinearCode(K, n, k);
        if IsHermDual(C) then
            return C;
        end if;
    end for;
    return ZeroCode(K, n);    
end intrinsic;

intrinsic GenerateLinearCodeReciprocalPairs(K::FldFin, n::RngIntElt, k::RngIntElt, maxTry::RngIntElt) -> CodeLinFld, CodeLinFld
{Generates a pair of linear codes C1 and C2 of length n and dimension k over the field K such that C1 and C2 are reciprocal pairs.}
    if maxTry lt 10 then
        maxTry := 10;
    end if;

    for i := 1 to maxTry div 10 do
        C1 := RandomLinearCode(K, n, k);

        for j := 1 to maxTry do
            C2 := RandomLinearCode(K, n, k);

            if HasIntersection(C1, C2) eq false and HasIntersection(C1, C2) eq false then
                return C1, C2;
            end if;

        end for;
    end for;

    return ZeroCode(K, n), ZeroCode(K, n);    
    
end intrinsic;

intrinsic CombineCodes(C::[CodeLinFld]) -> CodeLinFld
{Returns the vertical concatenation of the list of codes C1 and C2.}

// QC:=&+[C[i] : i in [1..s]];
    return &+[C[i] : i in [1..#C]];
end intrinsic;