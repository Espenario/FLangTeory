from REGEX_2_DFA.SyntaxTree import *
from REGEX_2_DFA.Automata import *


def create_token_queue(INPUT, flag):
    '''
    Process the input and converts it to a list containing the regex elements and alphabets.
    
    Args:
        INPUT: string, containing the input 

    Returns:
        list, containing the regex elements and alphabets.

    '''
    tokens = []
    id = ''
    if flag == 0:
        if INPUT[0] == '(' and INPUT[1] == '(':
            tokens.append(INPUT[0])
        elif INPUT[0] == '(':
            id += INPUT[0]
        for i in range(1,len(INPUT) - 1):
            if INPUT[i] in ['(', ')', '.', '*', '+','|'] and INPUT[i-1] in ['(', ')', '.', '*', '+','|'] and INPUT[i+1] in ['(', ')', '.', '*', '+','|']:          # 
                if id != '':
                    tokens.append(id)
                    id = ''
                tokens.append(INPUT[i])
            else:
                id = id + INPUT[i]        
        if id != '' and INPUT[-2] in ['(', ')', '.', '*', '+','|']:
            tokens.append(id)
            tokens.append(INPUT[-1]) 
        elif id != '':
            tokens.append(id + INPUT[-1])
        else:
            tokens.append(INPUT[-1])    #
        return tokens
    else:
        for i in range(len(INPUT)):
            if INPUT[i] in ['(', ')', '.', '*', '+','|']:          # 
                if id != '':
                    tokens.append(id)
                    id = ''
                tokens.append(INPUT[i])
            else:
                id = id + INPUT[i]        
        if id != '':
            tokens.append(id)    #
        return tokens


def create_postfix_token_queue(tokens):
    '''
    Creates the postfix representation of the regex (stored in a list). This postfix representation is later used to create the Syntax Tree.
    
    Args:
        tokens: list, containing the regex elements and alphabets 

    Returns:
        list, containing the regex elements and alphabets in a postfix manner.

    '''
    output_queue = []
    stack = []
    for token in tokens:
        if token == '(':
            stack.append('(')
        elif token == ')':
            while (len(stack) > 0 and stack[-1] != '('):
                output_queue.append(stack.pop())
            stack.pop()
        elif token == '*':
            stack.append(token)
        elif token == '.':
            while len(stack) > 0 and stack[-1] == '*':
                output_queue.append(stack.pop())
            stack.append(token)
        elif token == '|':
            while len(stack) > 0 and (stack[-1] == '*' or stack[-1] == '.'):
                output_queue.append(stack.pop())
            stack.append(token)
        else:
            output_queue.append(token)
    while (len(stack) > 0):
        output_queue.append(stack.pop())
    #print(output_queue)
    return output_queue


def read_input(path):
    '''
    Reads in the input which should be in the following format:
    <N, number of alphabets>
    <alphabet 1>
    <alphabet 2>
    <alphabet ...>
    <alphabet N>
    <REGEX>
    for more detail on the input please refer to InOut_Formatting.md
    
    Args:
        path: string, the path to the input file

    Returns:
        list, containing the alphabets
        string, containing the Regex
    '''
    alph = []
    file = open(path)
    lines = file.readlines()
    check = 0
    if lines[-1].rstrip() == 'Norm':
        check = 1
    file.close()
    for i in range(int(lines[0])):
        alph.append(lines[1 + i].strip())
    return alph, lines[int(lines[0]) + 1].strip(), check

non_symbols = ['+', '*', '.', '(', ')','|']

def add_concat(regex):
    global non_symbols
    l = len(regex)
    res = []
    for i in range(l - 1):
        res.append(regex[i])
        if regex[i] not in non_symbols:
            if regex[i + 1] not in non_symbols or regex[i + 1] == '(':
                res += '.'
        if regex[i] == ')' and regex[i + 1] == '(':
            res += '.'
        if regex[i] == '*' and regex[i + 1] == '(':
            res += '.'
        if regex[i] == '*' and regex[i + 1] not in non_symbols:
            res += '.'
        if regex[i] == ')' and regex[i + 1] not in non_symbols:
            res += '.'

    res += regex[l - 1]
    #print(res, '+++++++++')
    return res


def regex2DFA(path):
    '''
    Computes the DFA of a regular expression
    
    Args:
        path: string, the path to the input file

    Returns:
        None
    '''
    # 1. Reading the input
    ALPH, INPUT,flag = read_input(path)
    # 2. Getting the tokens
    tokens = create_token_queue(INPUT, flag)
    #print(tokens)
    # 3. Converting the tokens to post-order format
    post = create_postfix_token_queue(tokens)
    # 4. Creating the tree
    t = Tree(post)
    #print(t)
    # 5. Creating the DFA
    #print(ALPH, '_______________________')
    d = DFA(ALPH, t)
    # 6. Printing the results
    #print(INPUT)
    #print(t)
    #print(d)
    #for state in d.states:
    #    state.final = not(state.final)
    #print(d)
    return d

if __name__ == '__main__':
    regex2DFA('begin_regex.txt')

