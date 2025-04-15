/* 

  function to convert a linear code over an extension field into a quasi-cyclic code

  Markus Grassl
  markus.grassl@ug.edu.pl

  v1.2: 2023-01-26
  
  v1.1: 2020-11-04
        - added functions related to the trace formula (see below)
	- corrected the confusion about the reversal of some vectors
	  now the reciprocal polynomial is used to obtain the corresponding idempotent generator
 
  v1.0: 2020-11-01
        - initial version
	


*/


intrinsic ConjugateReciprocalPolynomial(f::RngUPolElt[FldFin])->RngUPolElt
{}
  q2:=#CoefficientRing(f);
  fl,q:=IsSquare(q2);
  if not fl then
    error("The coefficient ring must be a quadratic extension");
  end if;
  return Normalize(Polynomial([c^q:c in Reverse(Eltseq(f))]));
end intrinsic;


intrinsic IdempotentExpansionCode(C::CodeLinFld,n::RngIntElt) -> CodeLinFld
{ Given a linear code C over GF(q^m) = ext<GF(q)|f>, return a code
whose codewords are obtained from those of C by expanding each
coordinate in GF(q^m) as a vector of the primitive cyclic code of
length n over GF(q) using its idempotent. }

    // note that we assume that the alphabet of C is a proper extension of its base field
    //   when the polynomial f above has degree 1, the results will be a code over the prime field,
    //   but only when the defining polynomial of is a divisor of x^n-1
    F := Alphabet(C);

    if Dimension(C) eq 0 then
      return ZeroCode(BaseField(F),n*Length(C));
    end if;

    f0 := DefiningPolynomial(F);
    m := Degree(f0);
    basis := [F.1^i: i in [0..m-1]];

    require (Parent(f0).1^n-1) mod f0 eq 0: "The defining polynomial of the alphabet of C must be a divisor of x^n-1";

    C0 := Dual(CyclicCode(n,ReciprocalPolynomial(f0)));
    g0 := Idempotent(C0);

    v0 := Vector([Coefficient(g0,i): i in [0..n-1]]);
    g0 := Matrix([Rotate(v0,i): i in [0..m-1]]);

    G:=Matrix([&cat[Eltseq(Vector(Eltseq(x))*g0):x in Eltseq(a*v)]:a in basis,v in Generators(C)]);
    return LinearCode(G);
    
end intrinsic;

intrinsic IdempotentExpansionCode(C::CodeLinFld,n::RngIntElt,f0::RngUPolElt[FldFin]) -> CodeLinFld
{ Given a linear code C over GF(q^m) = ext<GF(q)|f0>, return a code
whose codewords are obtained from those of C by expanding each
coordinate in GF(q^m) as a vector of the primitive cyclic code of
length n over GF(q) using its idempotent. }

    F := Alphabet(C);
    F0 := CoefficientRing(f0);

    if Dimension(C) eq 0 then
      return ZeroCode(F0,n*Length(C));
    end if;

    m := Degree(f0);
    require Characteristic(F) eq Characteristic(F0) and Degree(F,F0) eq m: 
      "The degree of the alphabet of the code C over the cofficient ring of the polynomial f0";
    Embed(F0,F);
    basis := [F.1^i: i in [0..m-1]];

    require (Parent(f0).1^n-1) mod f0 eq 0: "The polynomial f0 must be a divisor of x^n-1";

    C0 := Dual(CyclicCode(n,ReciprocalPolynomial(f0)));
    g0 := Idempotent(C0);

    v0 := Vector([Coefficient(g0,i): i in [0..n-1]]);
    g0 := Matrix([Rotate(v0,i): i in [0..m-1]]);

    G:=Matrix([&cat[Eltseq(Vector(Eltseq(x,F0))*g0):x in Eltseq(a*v)]:a in basis,v in Generators(C)]);
    return LinearCode(G);
    
end intrinsic;


/*

  the following functions are related to

  C. Guneri and F. Ozbudak,
  "The Concatenated Structure of Quasi-Cyclic Codes and an Improvement of Jensen's Bound,"
  in IEEE Transactions on Information Theory, vol. 59, no. 2, pp. 979-985, Feb. 2013,
  doi: 10.1109/TIT.2012.2225823.

  in particular the mappings in eq. (3.1)

*/


intrinsic ExtFieldToCylicCodePolynomial(delta::FldFinElt,n::RngIntElt)->RngUPolElt
{Map an element of an extension field to a polynomial in the corresponding irreducible cyclic code of length n in its polynomial reprsentation.}

// the mapping yields an additive and multiplicative isomorphism phi with
//    phi(a*b) = (phi(a) * phi(b)) mod f0
// where f0 is the defining polynomial of the extension field

  F:=Parent(delta);
  F0:=BaseField(F);

  alpha:=F.1;

  require alpha^n eq 1: "The defining polynomial of the parent of delta must be a divisor of x^n.";

  return 1/F0!n*Polynomial([Trace(delta*alpha^-k,F0):k in [0..n-1]]);
  
end intrinsic;


intrinsic ExtFieldToCylicCodeVector(delta::FldFinElt,n::RngIntElt)->ModTupFldElt
{Map an element of an extension field to a vector to the corresponding  irreducible cyclic code of length n}

  F:=Parent(delta);
  F0:=BaseField(F);

  alpha:=F.1;

  require alpha^n eq 1: "The defining polynomial of the parent of delta must be a divisor of x^n.";

  return 1/F0!n*Vector([Trace(delta*alpha^-k,F0):k in [0..n-1]]);
  
end intrinsic;



intrinsic TraceExpansionCode(C::CodeLinFld,n::RngIntElt) -> CodeLinFld
{Return the quasi-cyclic code obtained by expanding the elements of the alphabet of the code C as vectors in the corresponding irreducible cyclic codes via the trace formula.}

  F:=Alphabet(C);
  F0:=BaseField(F);
  f0:=DefiningPolynomial(F);

  if Dimension(C) eq 0 then
    return ZeroCode(F0,n*Length(C));
  end if;

  m := Degree(f0);
  basis := [F.1^i: i in [0..m-1]];

  require (Parent(f0).1^n-1) mod f0 eq 0: "The polynomial f0 must be a divisor of x^n-1";

/*
  fl,alpha:=HasRoot(f0,F);
  require fl:"The polynomial f0 does not have a root in the alphabet of the code C";
*/

  alpha:=F.1;


  G:=Matrix([[Trace(a*b*alpha^-k,F0):k in [0..n-1],a in Eltseq(g)]:b in basis,g in Generators(C)]);
  return LinearCode(G);
  
end intrinsic;


intrinsic TraceExpansionCode(C::CodeLinFld,n::RngIntElt,f0::RngUPolElt[FldFin]) -> CodeLinFld
{Return the quasi-cyclic code obtained by expanding the elements of the alphabet of the code C as vectors in the corresponding irreducible cyclic codes via the trace formula. The additional argument f0 is used as the defining polynomial for the extension field.}

  F:=Alphabet(C);
  F0:=CoefficientRing(f0);

  if Dimension(C) eq 0 then
    return ZeroCode(F0,n*Length(C));
  end if;

  m := Degree(f0);
  require Characteristic(F) eq Characteristic(F0) and Degree(F,F0) eq m: 
    "The degree of the alphabet of the code C over the cofficient ring of the polynomial f0";
  Embed(F0,F);
  basis := [F.1^i: i in [0..m-1]];

  require (Parent(f0).1^n-1) mod f0 eq 0: "The polynomial f0 must be a divisor of x^n-1";

  // use a fixed root of the polynomial; otherwise the result might be indeterministic
  aa,bb:=GetSeed();
  SetSeed(1);
  fl,alpha:=HasRoot(f0,F);assert Evaluate(f0,alpha) eq 0;
  SetSeed(aa,bb);

  require fl:"The polynomial f0 does not have a root in the alphabet of the code C";

  G:=Matrix([[Trace(a*b*alpha^-k,F0):k in [0..n-1],a in Eltseq(g)]:b in basis,g in Generators(C)]);
  return LinearCode(G);
  
end intrinsic;


intrinsic TraceExpansionCodeOLD(C::CodeLinFld,F0::FldFin,n::RngIntElt,alpha::FldFinElt) -> CodeLinFld
{Return the quasi-cyclic code over F0 obtained by expanding the elements of the alphabet of the code C as vectors in the corresponding irreducible cyclic codes via the trace formula. The additional argument alpha is used in the trace formula.}

  F:=Alphabet(C);
  F1:=Parent(alpha);

  if Dimension(C) eq 0 then
    return ZeroCode(F0,n*Length(C));
  end if;

  require #F mod #F0 eq 0:
    "The field F0 must be a subfield of the alphabet of the code C";
  Embed(F0,F);

  F1:=sub<F1|F0.1,alpha>; // make sure that alpha is in the minimal field containing F0

  require #F mod #F1 eq 0:
    "The element alpha must lie in a subfield of the alphabet of the code C";
  Embed(F1,F);

  alpha:=F1!alpha;

//  require alpha^n eq 1:
//    "The element alpha must be an n-th root of unity";


  m := Degree(F) div Degree(F0);
  basis := [alpha^i: i in [0..m-1]];

  G:=Matrix([[Trace(a*b*alpha^-k,F0):k in [0..n-1],a in Eltseq(g)]:b in basis,g in Generators(C)]);

  return LinearCode(G),G;
  
end intrinsic;


intrinsic TraceExpansionCode(C::CodeLinFld,F0::FldFin,n::RngIntElt,alpha::FldFinElt) -> CodeLinFld
{Return the quasi-cyclic (or quasi-twisted) code over F0 obtained by expanding the elements of the alphabet of the code C as vectors in the corresponding irreducible (consta) cyclic codes via the trace formula. The additional argument alpha is used in the trace formula.}

  F:=Alphabet(C);
  F1:=Parent(alpha);

  if Dimension(C) eq 0 then
    return ZeroCode(F0,n*Length(C));
  end if;

  require #F mod #F0 eq 0:
    "The field F0 must be a subfield of the alphabet of the code C";
  Embed(F0,F);

  F1:=sub<F1|F0.1,alpha>; // make sure that alpha is in the minimal field containing F0

  require #F mod #F1 eq 0:
    "The element alpha must lie in a subfield of the alphabet of the code C";
  Embed(F1,F);

  alpha:=F1!alpha;

// should we check for the order of alpha?

  m := Degree(F) div Degree(F0);
  basis := [alpha^i: i in [0..m-1]];

  G:=Matrix([[Trace(a*b*alpha^-k,F0):k in [0..n-1],a in Eltseq(g)]:b in basis,g in Generators(C)]);

  return LinearCode(G),G;
  
end intrinsic;



intrinsic TraceExpansionCode(C::CodeLinFld,F0::FldFin,n::RngIntElt,alpha::FldFinElt,basis::[FldFinElt]) -> CodeLinFld
{Return the quasi-cyclic code over F0 obtained by expanding the elements of the alphabet of the code C as vectors in the corresponding irreducible cyclic codes via the trace formula. The additional argument alpha is used in the trace formula.}

  F:=Alphabet(C);
  F1:=Parent(alpha);

  if Dimension(C) eq 0 then
    return ZeroCode(F0,n*Length(C));
  end if;

  require #F mod #F0 eq 0:
    "The field F0 must be a subfield of the alphabet of the code C";
  Embed(F0,F);

  F1:=sub<F1|F0.1,alpha>; // make sure that alpha is in the minimal field containing F0

  require #F mod #F1 eq 0:
    "The element alpha must lie in a subfield of the alphabet of the code C";
  Embed(F1,F);

  alpha:=F1!alpha;

  require alpha^n eq 1:
    "The element alpha must be an n-th root of unity";


  m := Degree(F) div Degree(F0);

  G:=Matrix([[Trace(a*b*alpha^-k,F0):k in [0..n-1],a in Eltseq(g)]:b in basis,g in Generators(C)]);

  return LinearCode(G),G;
  
end intrinsic;


/* ---------------------------------------------------------------------------------------------------- */
/* auxilliary functions 										*/
/* ---------------------------------------------------------------------------------------------------- */

intrinsic ChangeRing(C::Code,R::FldFin)->Code
{Return the code generated by changing the generator matrix of C to the ring R}
  return LinearCode(ChangeRing(GeneratorMatrix(C),R));
end intrinsic;

