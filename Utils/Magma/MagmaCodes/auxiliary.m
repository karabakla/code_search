/* some experimental auxiliary function related to the project
 
   quantum construction X applied to QC & QT codes


   Markus Grassl <markus.grassl@ug.edu.pl>

   v1..1 2023-03-21 changed the value of 'e_max' in 'generate_magma_code' from 1/2 to 1/3 as otherwise we might get wrong results for codes [[n,0,d]]_q
   v1.2 2023-03-19 added functions related to the symplectic case and CSS-like constructions
   v1.1 2023-03-03 corrected typo QuasiTwistedCycliccode
   v1.0 2023-02-11
  

*/

intrinsic generate_magma_code(Q::CodeQuantum:candidate:=false,e_max:=Length(Q) div 3) -> MonStgElt
{Generates Magma code for a quantum code that is obtained via QuantumQonstructionX from a linear quasi-cyclic or quasi-twisted cyclic code over GF(q^2).
When candidate is set to true, computing the minimum distance is omitted.}
  fl_qc:=exists(qc){qc:i in [Length(Q)+1..Length(Q)-e_max by -1]|myIsQuasiCyclic(qc) where qc:=PunctureCode(LinearCode(StabilizerCode(Q)),{i..Length(Q)})};
  if not fl_qc then
    fl_qt:=exists(qt){qc:i in [Length(Q)+1..Length(Q)-e_max by -1]|myIsQuasiTwistedCyclic(qc) where qc:=PunctureCode(LinearCode(StabilizerCode(Q)),{i..Length(Q)})};
  end if;
  if not (fl_qc or fl_qt) then
    error "cannot find related quasi-cyclic or quasi-twisted cyclic code";
  end if;
  if candidate then
    name:=Sprintf("qecc_%o_%o_d_%o",Length(Q),Dimension(Q),Isqrt(#Alphabet(Q)));
  else
    name:=Sprintf("qecc_%o_%o_%o_%o",Length(Q),Dimension(Q),MinimumWeight(Q:Method:="Zimmermann"),Isqrt(#Alphabet(Q)));
  end if;
  K<w>:=Alphabet(Q);
  if IsPrime(#K) then
    field_gen:="";
  else
    field_gen:=Sprintf(" where w:=Roots(Polynomial(GF(%o),%o))[1,1]",#K,Eltseq(DefiningPolynomial(K)));
  end if;
  P<x>:=PolynomialRing(K);
  variable:=Sprintf(" where x:=PolynomialRing(GF(%o)).1",#K);
  if fl_qc then
    gens:=GeneratorPolynomialMatrix(qc);
    if Nrows(gens) eq 1 then
      code:=Sprintf("QuasiCyclicCode(%o,%o)",Length(qc),Eltseq(gens));
    else
      code:=Sprintf("QuasiCyclicCode(%o,%o,%o)",Length(qc),Eltseq(gens),Nrows(gens));
    end if;
    if Length(Q) eq Length(qc) then
      code:="QuantumCode(" cat code cat ")" cat variable cat field_gen cat ";";
    else
      code:="QuantumConstructionX(" cat code cat ")" cat variable cat field_gen cat ";";
    end if;
  elif fl_qt then
    gens:=GeneratorPolynomialMatrix(qt);
    _,L_alpha:=myIsQuasiTwistedCyclic(qt);
    if #Set(L_alpha) ne 1 then
      error "only implemented for a uniform shift constant";
    end if;
    if Nrows(gens) eq 1 then
      code:=Sprintf("QuasiTwistedCyclicCode(%o,%o,GF(%o)!%o)",Length(qt),Eltseq(gens),#Alphabet(qt),L_alpha[1]);
    else
      code:="&+" cat Sprint([Sprintf("QuasiTwistedCyclicCode(%o,%o,GF(%o)!%o)",Length(qt),Eltseq(gens[i]),#Alphabet(qt),L_alpha[1]):i in [1..Nrows(gens)]]);
    end if;
    if Length(Q) eq Length(qt) then
      code:="QuantumCode(" cat code cat ")" cat variable cat field_gen cat ";";
    else
      code:="QuantumConstructionX(" cat code cat ")" cat variable cat field_gen cat ";";
    end if;
  end if;
  return name cat ":=" cat code;
end intrinsic;

intrinsic generate_magma_code(Q::CodeQuantum,C::Code:candidate:=false) -> MonStgElt
{Generates Magma code for a quantum code Q of length n that is obtained via QuantumQonstructionX from the quasi-cyclic or quasi-twisted cyclic code C of length 2n.
When candidate is set to true, computing the minimum distance is omitted.}
require Q cmpeq QuantumConstructionX(C:ExtendedFormat): "The code Q does not match the one obtained from the code C";
  fl_qc:=myIsQuasiCyclic(C);
  if not fl_qc then
    fl_qt:=myIsQuasiTwistedCyclic(C);
  end if;
  if not (fl_qc or fl_qt) then
    error("The code C is not know to be quasi-cyclic or quasi-twisted cyclic");
  end if;
  if candidate then
    name:=Sprintf("qecc_%o_%o_d_%o",Length(Q),Dimension(Q),Isqrt(#Alphabet(Q)));
  else
    name:=Sprintf("qecc_%o_%o_%o_%o",Length(Q),Dimension(Q),MinimumWeight(Q:Method:="Zimmermann"),Isqrt(#Alphabet(Q)));
  end if;
  K<w>:=Alphabet(C);
  if IsPrime(#K) then
    field_gen:="";
  else
    field_gen:=Sprintf(" where w:=Roots(Polynomial(GF(%o),%o))[1,1]",#K,Eltseq(DefiningPolynomial(K)));
  end if;
  P<x>:=PolynomialRing(K);
  variable:=Sprintf(" where x:=PolynomialRing(GF(%o)).1",#K);
  if fl_qc then
    gens:=GeneratorPolynomialMatrix(C);
    if Nrows(gens) eq 1 then
      code:=Sprintf("QuasiCyclicCode(%o,%o)",Length(C),Eltseq(gens));
    else
      code:=Sprintf("QuasiCyclicCode(%o,%o,%o)",Length(C),Eltseq(gens),Nrows(gens));
    end if;
    if Length(Q) eq Length(C) div 2 then
      code:="QuantumCode(" cat code cat ":ExtendedFormat)" cat variable cat field_gen cat ";";
    else
      code:="QuantumConstructionX(" cat code cat ":ExtendedFormat)" cat variable cat field_gen cat ";";
    end if;
  elif fl_qt then
    gens:=GeneratorPolynomialMatrix(C);
    _,L_alpha:=myIsQuasiTwistedCyclic(C);
    if #Set(L_alpha) ne 1 then
      error "only implemented for a uniform shift constant";
    end if;
    if Nrows(gens) eq 1 then
      code:=Sprintf("QuasiTwistedCyclicCode(%o,%o,GF(%o)!%o)",Length(C),Eltseq(gens),#Alphabet(C),L_alpha[1]);
    else
      code:="&+" cat Sprint([Sprintf("QuasiTwistedCyclicCode(%o,%o,GF(%o)!%o)",Length(C),Eltseq(gens[i]),#Alphabet(C),L_alpha[1]):i in [1..Nrows(gens)]]);
    end if;
    if Length(Q) eq Length(C) div 2 then
      code:="QuantumCode(" cat code cat ":ExtendedFormat)" cat variable cat field_gen cat ";";
    else
      code:="QuantumConstructionX(" cat code cat ":ExtendedFormat)" cat variable cat field_gen cat ";";
    end if;
  end if;
  return name cat ":=" cat code;
end intrinsic;


intrinsic generate_magma_code(Q::CodeQuantum,C1::Code,C2::Code:candidate:=false) -> MonStgElt
{Generates Magma code for a quantum code Q of length n that is obtained via QuantumQonstructionX using a-CSS like construction from the pair of  quasi-cyclic or quasi-twisted cyclic codes C1 and C2.
When candidate is set to true, computing the minimum distance is omitted.}
require Q cmpeq QuantumConstructionX(DirectSum(C1,C2):ExtendedFormat): "The code Q does not match the one obtained from the codes C1 and C2";
  fl_qc1:=myIsQuasiCyclic(C1);
  fl_qc2:=myIsQuasiCyclic(C2);
  fl_qt1:=myIsQuasiTwistedCyclic(C1);
  fl_qt2:=myIsQuasiTwistedCyclic(C2);
  if not (fl_qc1 and fl_qc1 or fl_qt2 and fl_qt2) then
    error("The codes C1 and C2 are not knowm  to be both quasi-cyclic or quasi-twisted cyclic");
  end if;
  if candidate then
    name:=Sprintf("qecc_%o_%o_d_%o",Length(Q),Dimension(Q),Isqrt(#Alphabet(Q)));
  else
    name:=Sprintf("qecc_%o_%o_%o_%o",Length(Q),Dimension(Q),MinimumWeight(Q:Method:="Zimmermann"),Isqrt(#Alphabet(Q)));
  end if;
  K<w>:=Alphabet(C1);
  if IsPrime(#K) then
    field_gen:="";
  else
    field_gen:=Sprintf(" where w:=Roots(Polynomial(GF(%o),%o))[1,1]",#K,Eltseq(DefiningPolynomial(K)));
  end if;
  P<x>:=PolynomialRing(K);
  variable:=Sprintf(" where x:=PolynomialRing(GF(%o)).1",#K);
  if fl_qc1 then
    gens1:=GeneratorPolynomialMatrix(C1);
    gens2:=GeneratorPolynomialMatrix(C2);
    if Nrows(gens1) eq 1 then
      code1:=Sprintf("QuasiCyclicCode(%o,%o)",Length(C1),Eltseq(gens1));
    else
      code1:=Sprintf("QuasiCyclicCode(%o,%o,%o)",Length(C1),Eltseq(gens1),Nrows(gens1));
    end if;
    if Nrows(gens2) eq 1 then
      code2:=Sprintf("QuasiCyclicCode(%o,%o)",Length(C2),Eltseq(gens2));
    else
      code2:=Sprintf("QuasiCyclicCode(%o,%o,%o)",Length(C2),Eltseq(gens2),Nrows(gens2));
    end if;
    if Length(Q) eq Length(C1) then
      code:="CSSCode(Dual(" cat code2 cat ")," cat code1 cat ")" cat variable cat field_gen cat ";";
    else
      code:="QuantumConstructionX(DirectSum(" cat code1 cat "," cat code2 cat "):ExtendedFormat)" cat variable cat field_gen cat ";";
    end if;
  elif fl_qt1 then
    gens1:=GeneratorPolynomialMatrix(C1);
    gens2:=GeneratorPolynomialMatrix(C2);
    _,L_alpha1:=myIsQuasiTwistedCyclic(C1);
    _,L_alpha2:=myIsQuasiTwistedCyclic(C2);
    if #Set(L_alpha1) ne 1 or #Set(L_alpha2) ne 1 then
      error "only implemented for a uniform shift constant";
    end if;
    if Nrows(gens1) eq 1 then
      code1:=Sprintf("QuasiTwistedCyclicCode(%o,%o,GF(%o)!%o)",Length(C1),Eltseq(gens1),#Alphabet(C1),L_alpha1[1]);
    else
      code1:="&+" cat Sprint([Sprintf("QuasiTwistedCyclicCode(%o,%o,GF(%o)!%o)",Length(C1),Eltseq(gens1[i]),#Alphabet(C1),L_alpha1[1]):i in [1..Nrows(gens1)]]);
    end if;
    if Nrows(gens2) eq 1 then
      code2:=Sprintf("QuasiTwistedCyclicCode(%o,%o,GF(%o)!%o)",Length(C2),Eltseq(gens2),#Alphabet(C1),L_alpha2[1]);
    else
      code2:="&+" cat Sprint([Sprintf("QuasiTwistedCyclicCode(%o,%o,GF(%o)!%o)",Length(C2),Eltseq(gens2[i]),#Alphabet(C2),L_alpha2[1]):i in [1..Nrows(gens2)]]);
    end if;
    if Length(Q) eq Length(C1) then
      code:="CSSCode(Dual(" cat code2 cat ")," cat code1 cat ")" cat variable cat field_gen cat ";";
    else
      code:="QuantumConstructionX(DirectSum(" cat code1 cat "," cat code2 cat "):ExtendedFormat)" cat variable cat field_gen cat ";";
    end if;
  end if;
  return name cat ":=" cat code;
end intrinsic;


intrinsic generate_magma_code_QC_QT(C::CodeLinFld:candidate:=false) -> MonStgElt
{Generates Magma code for quasi-cyclic or quasi-twisted cyclic code.
When candidate is set to true, computing the minimum distance is omitted.}
  fl_qc:=myIsQuasiCyclic(C);
  if not fl_qc then
  fl_qt,qt:=myIsQuasiTwistedCyclic(C);
  end if;
  if not (fl_qc or fl_qt) then
    error "cannot identify the code as being quasi-cyclic or quasi-twisted cyclic";
  end if;
  if candidate then
    name:=Sprintf("c_%o_%o_d_%o",Length(C),Dimension(C),#Alphabet(C));
  else
    name:=Sprintf("c_%o_%o_%o_%o",Length(C),Dimension(C),MinimumWeight(C:Method:="Zimmermann"),#Alphabet(C));
  end if;
  K<w>:=Alphabet(C);
  if IsPrime(#K) then
    field_gen:="";
  else
    field_gen:=Sprintf(" where w:=Roots(Polynomial(GF(%o),%o))[1,1]",#K,Eltseq(DefiningPolynomial(K)));
  end if;
  P<x>:=PolynomialRing(K);
  variable:=Sprintf(" where x:=PolynomialRing(GF(%o)).1",#K);
  if fl_qc then
    gens:=GeneratorPolynomialMatrix(C);
    if Nrows(gens) eq 1 then
      code:=Sprintf("QuasiCyclicCode(%o,%o)",Length(C),Eltseq(gens));
    else
      code:=Sprintf("QuasiCyclicCode(%o,%o,%o)",Length(C),Eltseq(gens),Nrows(gens));
    end if;
  elif fl_qt then
    gens:=GeneratorPolynomialMatrix(C);
    _,L_alpha:=myIsQuasiTwistedCyclic(C);
    if #Set(L_alpha) ne 1 then
      error "only implemented for a uniform shift constant";
    end if;
    if Nrows(gens) eq 1 then
      code:=Sprintf("QuasiTwistedCyclicCode(%o,%o,GF(%o)!%o)",Length(C),Eltseq(gens),#Alphabet(C),L_alpha[1]);
    else
      code:="&+" cat Sprint([Sprintf("QuasiTwistedCyclicCode(%o,%o,GF(%o)!%o)",Length(C),Eltseq(gens[i]),#Alphabet(C),L_alpha[1]):i in [1..Nrows(gens)]]);
    end if;
  end if;
return name cat ":=" cat code cat variable cat field_gen cat ";";
end intrinsic;



intrinsic related_QC_QT_code(Q::CodeQuantum:e_max:=Length(Q) div 2) -> CodeFld
{Determines whether a quantum code is obtained via QuantumQonstructionX from a quasi-cyclic or quasi-twisted cyclic code, and returns that code
When candidate is set to true, computing the minimum distance is omitted.}
  fl_qc:=exists(qc){qc:i in [Length(Q)+1..Length(Q)-e_max by -1]|myIsQuasiCyclic(qc) where qc:=PunctureCode(LinearCode(StabilizerCode(Q)),{i..Length(Q)})};
  if fl_qc then
     _:=myIsQuasiCyclic(qc);
    return qc;
  else
    fl_qt:=exists(qt){qc:i in [Length(Q)+1..Length(Q)-e_max by -1]|myIsQuasiTwistedCyclic(qc) where qc:=PunctureCode(LinearCode(StabilizerCode(Q)),{i..Length(Q)})};
    if fl_qt then
       _:=myIsQuasiTwistedCyclic(qt);
      return qt;
    else 
      error "cannot find related quasi-cyclic or quasi-twisted cyclic code";
    end if;
  end if;
end intrinsic;
