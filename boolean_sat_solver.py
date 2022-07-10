#!/usr/bin/env python3
"""Boolean satisfiability solving"""

import sys
sys.setrecursionlimit(10000)

def simplify_with_unit_clauses(formula, assignments):
    '''
    Given the literal assignments, return the formula.
    
    >>> cnf = [[('a', True), ('b', True), ('c', True)], [('a', False), ('f', True)], [('d', False), ('e', True), ('a', True), ('g', True)], [('h', False), ('c', True), ('a', False), ('f', True)]]
    >>> assignments = {"a": True}
    >>> simplify_with_unit_clauses(cnf, assignments)
    ([], True)
    
    >>> assignments = {"a": False}
    >>> simplify_with_unit_clauses(cnf, assignments)
    ([[('b', True), ('c', True)], [('d', False), ('e', True), ('g', True)]], False)
    
    >>> assignments = {"a": True, "f": True}
    >>> simplify_with_unit_clauses(cnf, assignments)
    ([], False)
    
    >>> assignments = {"a": True, "f": False}
    >>> print(simplify_with_unit_clauses(cnf, assignments))
    None
    
    '''
    simplified_formula = []
    exists_unit_clause = False
    
    for clause in formula:
        
        simplified_clause = []
        for variable, value in clause:
            
            # when the variable is already in assignments
            if variable in assignments:
                if assignments[variable] == value: # mathces
                    break 
                else:# doesn't match
                    pass
            
            # when the variable is NOT already in assignments
            else:
                simplified_clause.append((variable, value))
        else:
            if len(simplified_clause) == 0:
                return None
            
            elif len(simplified_clause) == 1: # unit clause!
                exists_unit_clause = True
                clause_var, clause_val = simplified_clause[0]
                assignments[clause_var] = clause_val
                continue
            
            elif len(simplified_clause) > 1:
                simplified_formula.append(simplified_clause)
        
    return simplified_formula, exists_unit_clause


def satisfying_assignment(formula):
    """
    Find a satisfying assignment for a given CNF formula.
    Returns that assignment if one exists, or None otherwise.

    >>> satisfying_assignment([])
    {}
    >>> x = satisfying_assignment([[('a', True), ('b', False), ('c', True)]])
    >>> x.get('a', None) is True or x.get('b', None) is False or x.get('c', None) is True
    True
    >>> satisfying_assignment([[('a', True)], [('a', False)]])
    """
    if len(formula) == 0:
        return {}
    
    if formula is None:
        return None
    
    variable, value = formula[0][0]
    
    
    def try_assignment(temp_assignment):
        '''
        Test if the variable and value assignment satisfied formula.
        Returns assignment if one exists, or None otherwise.
        '''
        
        exists_unit_clause = True
        simplified_formula = formula.copy()
        
        if simplified_formula is None:
            return None
        
        # continue testing out assignments when simplifying the formula
        while exists_unit_clause:
            try:
                simplified_formula, exists_unit_clause = simplify_with_unit_clauses(simplified_formula, temp_assignment)
            except TypeError:
                print("NoneType object encountered")
                return None
                    
        assignment = satisfying_assignment(simplified_formula)
        
        if assignment is not None:
            assignment.update(temp_assignment)
            return assignment
        
        return None
        
            
    for val in [value, not value]:
        assignment = try_assignment({variable:val})
        
        # try the alternate literal assignment
        if assignment is None:
            continue
        else:
            return assignment
    
    return None


def get_preferences(student_preferences):
    '''
    Rule 1: Students Only In Desired Sessions
    Return CNF list of tuples with student's preferences in form [(student_session, True)]
    '''
    all_pref = []
    for student in student_preferences.keys():
        student_pref = []
        for session in student_preferences[student]:
            student_pref.append((student+"_"+session, True))
        all_pref.append(student_pref)
    return all_pref

def get_combos(elts, length, prev=[]):
    '''
    Return list combos, containing all possible combinations with the given length
    from the list elts using recursion
    '''
    if len(prev) == length:
        return [prev]
    else:
        combos = []
        for i, val in enumerate(elts):
            prev_copy = prev.copy()
            prev_copy.append(val)
            combos += get_combos(elts[i+1:], length, prev_copy)
    return combos
        

def get_max_one_session(student_preferences, room_capacities):
    '''
    Rule 2: Each Student In Exactly One Session
    Return CNF list of tuples such that a student is in no more than one session
    '''
    students = list(student_preferences.keys())
    sessions = list(room_capacities.keys())
    
    sess_combos = get_combos(sessions, 2)
    
    max_one = []
    for student in students:
        for sess_combo in sess_combos:
            max_one.append([(student+"_"+session, False) for session in sess_combo])
    return max_one


def get_oversubscribed(student_preferences, room_capacities):
    '''
    Rule 3: No Oversubscribed Sessions
    Return CNF list of tuples such that the rooms do not exceed capacity
    '''
    students = list(student_preferences.keys())
    sessions = list(room_capacities.keys())
    
    oversubscribed = []
    for session in sessions:
        capacity = room_capacities[session]
        
        # only when the number of students exceed a room's capacity
        if len(students) > capacity:
            student_combos = get_combos(students, capacity+1)
            
            temp_oversubscribed = []
            for combo in student_combos:
                temp_oversubscribed.append([(student+"_"+session, False) for student in combo])
            
            oversubscribed.extend(temp_oversubscribed)
    return oversubscribed

def boolify_scheduling_problem(student_preferences, room_capacities):
    """
    Convert a quiz-room-scheduling problem into a Boolean formula.

    student_preferences: a dictionary mapping a student name (string) to a set
                         of room names (strings) that work for that student

    room_capacities: a dictionary mapping each room name to a positive integer
                     for how many students can fit in that room

    Returns: a CNF formula encoding the scheduling problem, as per the
             lab write-up

    We assume no student or room names contain underscores.
    """
    return get_preferences(student_preferences) + get_max_one_session(student_preferences, room_capacities) + get_oversubscribed(student_preferences, room_capacities)

if __name__ == '__main__':
    import doctest
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)
