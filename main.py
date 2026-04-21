# ==========================================
# 1. CORE DATA STRUCTURES
# ==========================================
# A formula can just be a string like "p & (q | ~r)" or a nested tuple: ('AND', 'p', ('OR', 'q', ('NOT', 'r')))
# A belief_base is just a dictionary: {formula: priority_score}

# Internal representation used after parsing:
# "p"                  -> atomic formula
# ('NOT', 'p')         -> negation
# ('AND', a, b)        -> conjunction
# ('OR', a, b)         -> disjunction
# ('IMP', a, b)        -> implication
# ('IFF', a, b)        -> equivalence

# belief_base format:
#   {formula_string: priority_score}

def create_empty_belief_base():
    return {}

def create_initial_belief_base():
    """
    Returns an inconsistent belief base for testing entailment and contraction.
    Format: {formula_string: priority_score}
    """
    
    return {
        "p": 10,           # True belief 1
        "q | r": 8,        # True belief 2 
        "s -> t": 5,       # True belief 3 
        "~p": 2            # Contradictory belief (clashes with "p")
    }

# Helper functions to identify formula types    
def is_atom(formula):
    return isinstance(formula, str)
# Note: In a more complete implementation, we would also want to handle parentheses 
# and operator precedence when parsing strings into the internal tuple representation. 
# For simplicity, we assume the input is already in the correct format or that parsing is handled separately.
def is_negation(formula):
    return isinstance(formula, tuple) and len(formula) == 2 and formula[0] == 'NOT'
# For binary operators, we check if it's a tuple of length 3 and the first element is one of the valid operators.
def is_binary(formula):
    return isinstance(formula, tuple) and len(formula) == 3 and formula[0] in ('AND', 'OR', 'IMP', 'IFF')
# We can also add specific checks for each operator if needed, e.g., is_conjunction, is_disjunction, etc.
def is_tuple_formula(formula):
    return isinstance(formula, tuple)

# Helper function to find the main operator in a formula string, ignoring parentheses
def find_main_operator(formula,operator):
    depth =0
    i=0
    while i<len(formula):
         char = formula[i]
         if char == '(':
                depth += 1
         elif char == ')':
                depth -= 1
         elif depth == 0:
             # Check if the operator matches at this position   
             if formula[i:i+len(operator)] == operator:
                 return i
         i+=1
    return -1
             

def has_outer_parentheses(formula):
    formula =formula.strip()
    if not (formula.startswith('(') and formula.endswith(')')):
        return False
    depth = 0
    for i, char in enumerate(formula):
        if char == '(':
            depth += 1
        elif char == ')':
            depth -= 1
            if depth == 0 and i != len(formula) - 1:
                return False
    return depth == 0
    

# For the sake of this assignment, we will assume that the input formulas are already in the correct internal tuple format.
def parse_formula(formula_str):
    """
    Converts a formula string into the internal tuple representation.

    Supported operators:
      ~   negation
      &   conjunction
      |   disjunction
      ->  implication

    Examples:
      "p"      -> "p"
      "~p"     -> ('NOT', 'p')
      "q | r"  -> ('OR', 'q', 'r')
      "s -> t" -> ('IMP', 's', 't')

    """
    if not isinstance(formula_str, str):
        return formula_str # Already in tuple form, return as is
    
    formula_str = formula_str.strip()
    
    # Remove outer parentheses if they exist
    while has_outer_parentheses(formula_str):
        formula_str = formula_str[1:-1].strip()
        
    # Implication
    idx = find_main_operator(formula_str,'->')
    if idx != -1:
        left = formula_str[:idx]
        right = formula_str[idx+2:]
        return ('IMP', parse_formula(left.strip()), parse_formula(right.strip()))
    # Disjunction
    idx = find_main_operator(formula_str,'|')
    if idx != -1:
        left = formula_str[:idx]
        right = formula_str[idx+1:]
        return ('OR', parse_formula(left.strip()), parse_formula(right.strip()))
    # Conjunction
    idx = find_main_operator(formula_str,'&')
    if idx != -1:
        left = formula_str[:idx]
        right = formula_str[idx+1:]
        return ('AND', parse_formula(left.strip()), parse_formula(right.strip()))
    # Negation
    if formula_str.startswith('~'):
        return ('NOT', parse_formula(formula_str[1:].strip()))
    
    # Atomic formula
    return formula_str  

# ==========================================
# 2. LOGICAL ENTAILMENT ENGINE
# ==========================================

def eliminate_implications(formula):
    """
    Recursively eliminates implications and biconditionals from the formula.
    """
    if is_atom(formula):
        return formula
    if is_negation(formula):
        return ('NOT', eliminate_implications(formula[1]))
    if is_binary(formula):
        op, left, right = formula
        left = eliminate_implications(left)
        right = eliminate_implications(right)
        if op == 'IMP':
            # A -> B is equivalent to ~A | B
            return ('OR', ('NOT', left), right)
        elif op == 'IFF':
            # A <-> B is equivalent to (A -> B) & (B -> A)
            return ('AND', 
                    ('OR', ('NOT', left), right), 
                    ('OR', ('NOT', right), left))
        else:
            return (op, left, right)
    return formula

def move_negations(formula):
    """
    Recursively moves negations inward using De Morgan's laws.
    """
    if is_atom(formula):
        return formula
    if is_negation(formula):
        inner = formula[1]
        if is_atom(inner):
            return formula
        if is_negation(inner):
            # ~~A is equivalent to A
            return move_negations(inner[1])
        if is_binary(inner):
            op, left, right = inner
            if op == 'AND':
                # ~(A & B) is equivalent to ~A | ~B
                return ('OR', move_negations(('NOT', left)), move_negations(('NOT', right)))
            elif op == 'OR':
                # ~(A | B) is equivalent to ~A & ~B
                return ('AND', move_negations(('NOT', left)), move_negations(('NOT', right)))
    if is_binary(formula):
        op, left, right = formula
        return (op, move_negations(left), move_negations(right))
    return formula

def distribute_or_over_and(formula):
    """
    Recursively distributes OR over AND to get CNF.
    """
    if is_atom(formula) or is_negation(formula):
        return formula
    if is_binary(formula):
        op, left, right = formula
        left = distribute_or_over_and(left)
        right = distribute_or_over_and(right)
        if op == 'OR':
            if is_binary(left) and left[0] == 'AND':
                # A | (B & C) is equivalent to (A | B) & (A | C)
                return ('AND', 
                        distribute_or_over_and(('OR', left[1], right)), 
                        distribute_or_over_and(('OR', left[2], right)))
            elif is_binary(right) and right[0] == 'AND':
                # (A & B) | C is equivalent to (A | C) & (B | C)
                return ('AND', 
                        distribute_or_over_and(('OR', left, right[1])), 
                        distribute_or_over_and(('OR', left, right[2])))
        return (op, left, right)
    return formula

def to_cnf(formula):
    """
    Converts a propositional formula string/tuple into Conjunctive Normal Form (CNF). 
    WE DONT NEED TO USE THIS IF WE DON'T WANT TO FOR THE ASSIGNMENT
    """
   # Parse the formula if it's a string
    if isinstance(formula, str):
        formula = parse_formula(formula)
   
   # Eliminate implications and biconditionals, move negations inward, and distribute OR over AND to get CNF.
    formula = eliminate_implications(formula)
   
   # Move NOT inward
    formula = move_negations(formula)
   
   # Distribute OR over AND
    formula = distribute_or_over_and(formula)
    return formula
   

def resolve(clause1, clause2):
    """
    Helper function to resolve two clauses.
    """
    pass # TODO: Implement resolution step

def check_entailment(belief_base, formula):
    """
    Checks if the given belief_base (dict) entails the formula.
    Returns True if entailed, False otherwise.
    """
    pass # TODO: Implement the full resolution-based entailment loop without packages


# ==========================================
# 3. BELIEF REVISION OPERATIONS
# ==========================================

def expand(belief_base, formula, priority):
    """
    Implementation of expansion of belief base.
    Returns a NEW dictionary representing the resulting/new belief base.
    """
    # Create a copy so we don't mutate the original dictionary
    new_bb = belief_base.copy() 
    # TODO: Add the formula and priority to new_bb
    return new_bb

def contract(belief_base, formula):
    """
    Implementation of contraction of belief base (based on a priority order on formulas).
    Returns a NEW dictionary representing the resulting/new belief base.
    """
    new_bb = belief_base.copy()
    # TODO: Implement contraction logic (e.g., partial meet contraction) using the priority values
    return new_bb

# ==========================================
# 4. TESTING AGM POSTULATES
# ==========================================

def test_agm_postulates():
    """
    You are requested to use the AGM postulates to test your algorithm.
    (Success, Inclusion, Vacuity, Consistency, and Extensionality).
    """
    # TODO: Set up initial belief base dictionaries and assert that the outputs 
    # of your expand, contract, and revise functions follow the rules.
    print("Testing AGM postulates...")
    pass

if __name__ == "__main__":
    # Example workflow
    my_belief_base = create_initial_belief_base()
    
    # print("Testing parse_formula:")
    # for f in my_belief_base:
    #     print(f, "->", parse_formula(f))
        
    # print(parse_formula ("s -> t"))
    # print (eliminate_implications(parse_formula ("s -> t")))
    # print(parse_formula("(p -> q) & (q -> p)"))
    
    test_formula =[
        "p",
        "~p",
        "q | r",
        "p & q",
        "s -> t",
        "~(p & q)",
        "~(p | q)",
        "(p & q) | r",
        "(p -> q) & (q -> p)"
        ]
    print ("=====================================")
    print ("Testing to_cnf:\n")
    for f in test_formula:
        print(f, "->", to_cnf(f))
        print ("=====================================")
        print("Original: ",f)
        print ("Parsed:", parse_formula(f))
        print ("CNF:", to_cnf(f))
        print("-" *40)
        
    test_agm_postulates()