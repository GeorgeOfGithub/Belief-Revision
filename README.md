# 02180 Intro to AI - Belief Revision Assignment

## Overview
This project implements a propositional belief revision engine from scratch. It uses an Object-Oriented Abstract Syntax Tree (AST) to represent logical formulas, a custom resolution-based entailment engine, and performs belief revision using Partial Meet Contraction and the Levi Identity.

## Prerequisites
* Python 3.x
* No external packages or libraries are required, per the assignment guidelines. The implementation uses only Python's standard library.

## How to Run the Code
To execute the engine and see the demonstration, open a terminal, navigate to the directory containing the source code, and run:

`python3 main.py`

## What to Expect in the Output
When you run the script, it will execute four main sections sequentially:

1. **AST TO_CNF PIPELINE**: Demonstrates the engine's ability to recursively parse formulas, eliminate implications, push negations inward (De Morgan's laws), and distribute OR over AND to correctly produce Conjunctive Normal Form (CNF) clauses.
2. **ENTAILMENT ENGINE**: Tests the resolution-based prover by converting a Knowledge Base and a negated query into CNF, then resolving clauses to find contradictions.
3. **AGENT LIFECYCLE DEMO**: Demonstrates the core belief revision operations. It creates an initial inconsistent belief base, contracts it by a specific formula to restore consistency using Partial Meet Contraction, and then revises it with new information.
4. **AGM POSTULATES**: Automatically tests the engine against the 5 AGM postulates (Success, Inclusion, Vacuity, Consistency, and Extensionality) to ensure theoretical correctness.

## Code Structure Highlights
* **Formula AST (main.py)**: Classes (`Symbol`, `Not`, `And`, `Or`, `Implies`, `BiImplies`) that encapsulate the logic for strict CNF conversions.
* **check_entailment()**: Implements proof by refutation via a custom resolution loop.
* **contract()**: Implements Partial Meet Contraction by generating maximal subsets of the belief base that do not entail the formula, scoring them based on epistemic priority, and intersecting the highest-scoring remainders.
* **revise()**: Implements revision using the Levi Identity.