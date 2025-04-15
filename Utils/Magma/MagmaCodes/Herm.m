intrinsic HermDual(C::CodeLinFld) -> CodeLinFld
{Returns the Hermitean dual of the code C.}
    local n,F,q,G,A;
    n:=Length(C);
    F:=Field(C);
    q:=Round(Sqrt(#F));
    G:=GeneratorMatrix(Dual(C));
    A:=RowSequence(G);
    for j:=1 to #A do
        for i:=1 to n do
            A[j][i]:=(A[j][i])^q;
        end for;
    end for;
    return LinearCode<F,n |A>;
end intrinsic;

intrinsic IsHermSelfOrthogonal(C::CodeLinFld) -> BoolElt
{Returns true if the code C is Hermitean self-orthogonal.}
    return C subset HermDual(C);
end intrinsic;

intrinsic Herm(C::CodeLinFld) -> CodeLinFld
{Returns the Hermitean code of the code C.}

    // local n,F,q,G,A;
    n:=Length(C);
    F:=Field(C);
    q:=Round(Sqrt(#F));
    G:=GeneratorMatrix(C);
    A:=RowSequence(G);
    for j:=1 to #A do
        for i:=1 to n do
            A[j][i]:=(A[j][i])^q;
        end for;
    end for;
    return LinearCode<F,n |A>;
end intrinsic;

intrinsic HermHull(C::CodeLinFld) -> CodeLinFld
{Returns the Hermitean hull of the code C.}
    return C meet HermDual(C);
end intrinsic;
