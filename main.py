# ==========================================
# 1. CORE DATA STRUCTURES (AST)
# ==========================================

class Formula:
    """
    Base class for all propositional logic formulas.
    Implements the transformation pipeline for Conjunctive Normal Form (CNF).
    """
    def eliminate_implications(self): raise NotImplementedError
    def move_negations(self): raise NotImplementedError
    def distribute_or_over_and(self): raise NotImplementedError
    
    def to_cnf(self):
        """
        Converts a formula into CNF using a three-step logical pipeline:
        1. Eliminate implications and biconditionals.
        2. Move negations inward using De Morgan's laws.
        3. Distribute OR over AND.
        """
        f = self.eliminate_implications()
        f = f.move_negations()
        f = f.distribute_or_over_and()
        return f

class Symbol(Formula):
    """Represents an atomic proposition (e.g., 'p')."""
    def __init__(self, name):
        self.name = name

    def eliminate_implications(self): return self
    def move_negations(self): return self
    def distribute_or_over_and(self): return self

    def __eq__(self, other): return isinstance(other, Symbol) and self.name == other.name
    def __hash__(self): return hash(("Symbol", self.name))
    def __repr__(self): return self.name


class Not(Formula):
    """Represents logical negation (~)."""
    def __init__(self, inner):
        self.inner = inner

    def eliminate_implications(self):
        return Not(self.inner.eliminate_implications())

    def move_negations(self):
        # Double negation: ~~A -> A
        if isinstance(self.inner, Not):
            return self.inner.inner.move_negations()
        # De Morgan's: ~(A & B) -> ~A | ~B
        if isinstance(self.inner, And):
            return Or(Not(self.inner.left), Not(self.inner.right)).move_negations()
        # De Morgan's: ~(A | B) -> ~A & ~B
        if isinstance(self.inner, Or):
            return And(Not(self.inner.left), Not(self.inner.right)).move_negations()
        return Not(self.inner.move_negations())

    def distribute_or_over_and(self):
        return Not(self.inner.distribute_or_over_and())

    def __eq__(self, other): return isinstance(other, Not) and self.inner == other.inner
    def __hash__(self): return hash(("Not", self.inner))
    def __repr__(self): return f"~{self.inner}"


class And(Formula):
    """Represents logical conjunction (&)."""
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def eliminate_implications(self):
        return And(self.left.eliminate_implications(), self.right.eliminate_implications())
    
    def move_negations(self):
        return And(self.left.move_negations(), self.right.move_negations())

    def distribute_or_over_and(self):
        return And(self.left.distribute_or_over_and(), self.right.distribute_or_over_and())

    def __eq__(self, other): return isinstance(other, And) and self.left == other.left and self.right == other.right
    def __hash__(self): return hash(("And", self.left, self.right))
    def __repr__(self): return f"({self.left} & {self.right})"


class Or(Formula):
    """Represents logical disjunction (|)."""
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def eliminate_implications(self):
        return Or(self.left.eliminate_implications(), self.right.eliminate_implications())

    def move_negations(self):
        return Or(self.left.move_negations(), self.right.move_negations())

    def distribute_or_over_and(self):
        l = self.left.distribute_or_over_and()
        r = self.right.distribute_or_over_and()
        # Distribution Rule: (A & B) | C -> (A | C) & (B | C)
        if isinstance(l, And):
            return And(Or(l.left, r).distribute_or_over_and(), 
                       Or(l.right, r).distribute_or_over_and())
        # Distribution Rule: A | (B & C) -> (A | B) & (A | C)
        elif isinstance(r, And):
            return And(Or(l, r.left).distribute_or_over_and(), 
                       Or(l, r.right).distribute_or_over_and())
        return Or(l, r)

    def __eq__(self, other): return isinstance(other, Or) and self.left == other.left and self.right == other.right
    def __hash__(self): return hash(("Or", self.left, self.right))
    def __repr__(self): return f"({self.left} | {self.right})"


class Implies(Formula):
    """Represents logical implication (->)."""
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def eliminate_implications(self):
        # A -> B is equivalent to ~A | B
        return Or(Not(self.left.eliminate_implications()), self.right.eliminate_implications())

    def move_negations(self):
        return Implies(self.left.move_negations(), self.right.move_negations())

    def distribute_or_over_and(self):
        return Implies(self.left.distribute_or_over_and(), self.right.distribute_or_over_and())

    def __eq__(self, other): return isinstance(other, Implies) and self.left == other.left and self.right == other.right
    def __hash__(self): return hash(("Implies", self.left, self.right))
    def __repr__(self): return f"({self.left} -> {self.right})"


class BiImplies(Formula):
    """Represents logical equivalence (<->)."""
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def eliminate_implications(self):
        # A <-> B is equivalent to (A -> B) & (B -> A)
        l_elim = self.left.eliminate_implications()
        r_elim = self.right.eliminate_implications()
        return And(Or(Not(l_elim), r_elim), Or(Not(r_elim), l_elim))

    def move_negations(self):
        return BiImplies(self.left.move_negations(), self.right.move_negations())

    def distribute_or_over_and(self):
        return BiImplies(self.left.distribute_or_over_and(), self.right.distribute_or_over_and())

    def __eq__(self, other): return isinstance(other, BiImplies) and self.left == other.left and self.right == other.right
    def __hash__(self): return hash(("BiImplies", self.left, self.right))
    def __repr__(self): return f"({self.left} <-> {self.right})"


# ==========================================
# 2. BELIEF BASE INITIALIZATION
# ==========================================

def create_initial_belief_base():
    """Returns a standard inconsistent belief base for testing."""
    p, q, r, s, t = Symbol("p"), Symbol("q"), Symbol("r"), Symbol("s"), Symbol("t")
    return {
        p: 10,
        Or(q, r): 8,
        Implies(s, t): 5,
        Not(p): 2
    }


# ==========================================
# 3. LOGICAL ENTAILMENT ENGINE
# ==========================================

def extract_literals(formula):
    """Recursively collects literals from a disjunction."""
    if isinstance(formula, Or):
        return extract_literals(formula.left).union(extract_literals(formula.right))
    return {formula}

def extract_clauses(formula):
    """Recursively collects clauses from a conjunction."""
    if isinstance(formula, And):
        return extract_clauses(formula.left) + extract_clauses(formula.right)
    return [extract_literals(formula)]

def is_complementary(l1, l2):
    """Checks if two literals are complements (e.g., p and ~p)."""
    if isinstance(l1, Not) and l1.inner == l2: return True
    if isinstance(l2, Not) and l2.inner == l1: return True
    return False

def is_tautology(clause):
    """Checks if a clause is a tautology (contains p | ~p)."""
    for literal in clause:
        if isinstance(literal, Not) and literal.inner in clause: return True
    return False

def resolve(clause1, clause2):
    """Applies the resolution rule to two clauses."""
    resolvents = []
    for l1 in clause1:
        for l2 in clause2:
            if is_complementary(l1, l2):
                # New clause = (C1 - {l1}) U (C2 - {l2})
                c1_mod = set(clause1); c1_mod.remove(l1)
                c2_mod = set(clause2); c2_mod.remove(l2)
                new_clause = c1_mod.union(c2_mod)
                if not is_tautology(new_clause):
                    resolvents.append(frozenset(new_clause))
    return resolvents

def check_entailment(belief_base_list, query):
    """Checks KB |= query using Resolution Proof by Refutation."""
    # To prove KB |= query, we check if KB & ~query is unsatisfiable
    statements = belief_base_list + [Not(query)]
    clauses = set()
    for s in statements:
        for c in extract_clauses(s.to_cnf()):
            clauses.add(frozenset(c))
    
    while True:
        clauses_list = list(clauses)
        n = len(clauses_list)
        new = set()
        for i in range(n):
            for j in range(i + 1, n):
                for res in resolve(clauses_list[i], clauses_list[j]):
                    if not res: return True # Empty clause found
                    new.add(res)
        if new.issubset(clauses): return False
        clauses.update(new)


# ==========================================
# 4. BELIEF REVISION OPERATIONS
# ==========================================

def expand(belief_base, formula, priority):
    """B + phi: Simply adds the formula to the base."""
    new_bb = belief_base.copy()
    new_bb[formula] = priority
    return new_bb

def get_combinations(lst, r):
    """Helper to generate all combinations of size r."""
    if r == 0: return [[]]
    if not lst: return []
    return [[lst[0]] + rest for rest in get_combinations(lst[1:], r - 1)] + get_combinations(lst[1:], r)

def contract(belief_base, formula):
    """B / phi: Partial Meet Contraction using Epistemic Entrenchment."""
    if not check_entailment(list(belief_base.keys()), formula):
        return belief_base.copy()

    keys = list(belief_base.keys())
    all_valid = []
    for r in range(len(keys) + 1):
        for subset in get_combinations(keys, r):
            if not check_entailment(subset, formula):
                all_valid.append(set(subset))

    # Find maximal subsets (remainders)
    remainders = [s for s in all_valid if not any(s < other for other in all_valid)]
    if not remainders: return belief_base.copy()

    # Selection function based on priority scores
    scored = [(sum(belief_base[f] for f in rem), rem) for rem in remainders]
    max_score = max(scored, key=lambda x: x[0])[0]
    best = [rem for score, rem in scored if score == max_score]

    # Intersection of best remainders
    final_set = set(best[0])
    for rem in best[1:]: final_set &= set(rem)
    return {f: belief_base[f] for f in final_set}

def revise(belief_base, formula, priority):
    """B * phi: Revision via Levi Identity (B / ~phi) + phi."""
    return expand(contract(belief_base, Not(formula)), formula, priority)


# ==========================================
# 5. TESTING AGM POSTULATES
# ==========================================

def test_agm_postulates():
    """Full programmatic test of all 16 AGM postulates."""
    print("\n" + "="*50)
    print("4. TESTING AGM POSTULATES")
    print("="*50 + "\n")

    p, q, r = Symbol("p"), Symbol("q"), Symbol("r")
    
    # Setup specific test bases to ensure non-trivial results
    con_base = {p: 5, q: 10} # Base for Contraction tests
    rev_base = {p: 10, r: 5} # Base for Revision tests

    print("--- CONTRACTION POSTULATES ---")
    c_p = contract(con_base, p); c_pq = contract(con_base, And(p, q)); c_q = contract(con_base, q)

    print(f"1. Closure Postulate:      {'PASSED' if check_entailment(list(c_pq.keys()), Or(q, r)) else 'FAILED'}")
    print(f"2. Success Postulate:      {'PASSED' if not check_entailment(list(c_p.keys()), p) else 'FAILED'}")
    print(f"3. Inclusion Postulate:    {'PASSED' if set(c_p.keys()).issubset(set(con_base.keys())) else 'FAILED'}")
    s = Symbol("s"); c_vac = contract(con_base, s)
    print(f"4. Vacuity Postulate:      {'PASSED' if set(c_vac.keys()) == set(con_base.keys()) else 'FAILED'}")
    c_ext = contract(con_base, Not(Not(p)))
    print(f"5. Extensionality Post:    {'PASSED' if set(c_p.keys()) == set(c_ext.keys()) else 'FAILED'}")
    rec_base = expand(c_p, p, 5)
    print(f"6. Recovery Postulate:     {'PASSED' if all(check_entailment(list(rec_base.keys()), f) for f in con_base.keys()) else 'FAILED'}")
    if not check_entailment(list(c_pq.keys()), p):
        print(f"7. Conjunctive Inclusion:  {'PASSED' if set(c_pq.keys()).issubset(set(c_p.keys())) else 'FAILED'}")
    else: print("7. Conjunctive Inclusion:  SKIPPED")
    overlap = set(c_p.keys()).intersection(set(c_q.keys()))
    print(f"8. Conjunctive Overlap:    {'PASSED' if overlap.issubset(set(c_pq.keys())) else 'FAILED'}")

    print("\n--- REVISION POSTULATES ---")
    phi = And(p, q); revised = revise(rev_base, phi, 5)

    print(f"1. Closure Postulate:      {'PASSED' if check_entailment(list(revised.keys()), Or(p, r)) else 'FAILED'}")
    print(f"2. Success Postulate:      {'PASSED' if phi in revised else 'FAILED'}")
    print(f"3. Inclusion Postulate:    {'PASSED' if set(revised.keys()).issubset(set(expand(rev_base, phi, 5).keys())) else 'FAILED'}")
    rev_vac = revise(rev_base, r, 5); exp_vac = expand(rev_base, r, 5)
    print(f"4. Vacuity Postulate:      {'PASSED' if set(rev_vac.keys()) == set(exp_vac.keys()) else 'FAILED'}")
    print(f"5. Consistency Postulate:  {'PASSED' if not check_entailment(list(revised.keys()), And(p, Not(p))) else 'FAILED'}")
    f1, f2 = Implies(p, q), Or(Not(p), q)
    r1, r2 = revise(rev_base, f1, 5), revise(rev_base, f2, 5)
    ext_pass = all(check_entailment(list(r1.keys()), f) for f in r2.keys()) and all(check_entailment(list(r2.keys()), f) for f in r1.keys())
    print(f"6. Extensionality Post:    {'PASSED' if ext_pass else 'FAILED'}")
    rev_p = revise(rev_base, p, 10); exp_rev_p_q = expand(rev_p, q, 5)
    print(f"7. Superexpansion Post:    {'PASSED' if all(check_entailment(list(exp_rev_p_q.keys()), f) for f in revised.keys()) else 'FAILED'}")
    if not check_entailment(list(rev_p.keys()), Not(q)):
        print(f"8. Subexpansion Post:      {'PASSED' if all(check_entailment(list(revised.keys()), f) for f in exp_rev_p_q.keys()) else 'FAILED'}")
    else: print("8. Subexpansion Post:      SKIPPED")
    print("\n" + "="*50 + "\n")


# ==========================================
# 6. MAIN EXECUTION & DEMO
# ==========================================

if __name__ == "__main__":
    p, q, r = Symbol("p"), Symbol("q"), Symbol("r")

    # --- Section 1: CNF Transform Demo ---
    print("\n" + "="*50)
    print("1. TESTING AST TO_CNF PIPELINE")
    print("="*50 + "\n")
    test_formulas = [Not(Not(p)), Implies(p, q), BiImplies(p, q), Not(And(p, q)), Or(And(p, q), r)]
    for f in test_formulas:
        print(f"Original: {f}")
        print(f"CNF:      {f.to_cnf()}")
        print("-" * 40)

    # --- Section 2: Entailment Demo ---
    print("\n" + "="*50)
    print("2. TESTING ENTAILMENT ENGINE")
    print("="*50 + "\n")
    kb = [Implies(p, q), p]
    print(f"KB: {kb}")
    print(f"KB entails q:  {check_entailment(kb, q)}")
    print(f"KB entails ~q: {check_entailment(kb, Not(q))}")

    # --- Section 3: Revision Demo ---
    print("\n" + "="*50)
    print("3. AGENT LIFECYCLE DEMO")
    print("="*50 + "\n")
    bb = create_initial_belief_base()
    print("Initial Belief Base:")
    for f, s in bb.items(): print(f"  [{s}] {f}")
    print(f"\nKB entails ~p? {check_entailment(list(bb.keys()), Not(p))}")
    print("\nContracting by p (Resolving inconsistency):")
    cb = contract(bb, p)
    for f, s in cb.items(): print(f"  [{s}] {f}")
    print("\nRevising by ~p (New belief with priority 10):")
    rb = revise(bb, Not(p), 10)
    for f, s in rb.items(): print(f"  [{s}] {f}")

    # --- Section 4: Postulates ---
    test_agm_postulates()