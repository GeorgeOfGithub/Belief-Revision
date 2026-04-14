# ==========================================
# 1. CORE DATA STRUCTURES
# ==========================================
# A formula can just be a string like "p & (q | ~r)" or a nested tuple: ('AND', 'p', ('OR', 'q', ('NOT', 'r')))
# A belief_base is just a dictionary: {formula: priority_score}

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

# ==========================================
# 2. LOGICAL ENTAILMENT ENGINE
# ==========================================

def to_cnf(formula):
    """
    Converts a propositional formula string/tuple into Conjunctive Normal Form (CNF). 
    WE DONT NEED TO USE THIS IF WE DON'T WANT TO FOR THE ASSIGNMENT
    """
    pass # TODO: Implement CNF conversion steps

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
    
    test_agm_postulates()