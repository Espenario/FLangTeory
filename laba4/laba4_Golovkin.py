class NonTerm():

    def __init__(self, value = None):
        self.value = value

    def get_type(self):
        return 'N'

class Rule():
    
    def __init__(self, value = None, nullable = None, children = None):
        self.value = value
        self.nullable = nullable
        self.children = children

    def get_value(self):
        return self.value.value
    

class Term():

    def __init__(self, value = None):
        self.value = value

    def get_type(self):
        return 'T'

class Grammar():

    def __init__(self, nonterm_elem_dict = None):
        self.nonterm_elem_dict = nonterm_elem_dict or {}

class Parser():
    
    def __init__(self, filename = None):
        self.filename = filename

    def parse(self):
        grammar = []
        appended_noterm = []
        index_dict = {}
        nullable_list = []
        f = open(self.filename, 'r')
        line = f.readline().split(' -> ')
        while line[0]: 
            rules = []
            #print(line[0], rules, '========')
            if not(line[1]):
                rules.append('$')
            else:
                rules = [elem.rstrip().replace(" ","") for elem in line[1].split('|')]
            nullable = False
            if '$' in rules:
                nullable_list.append(line[0])
                nullable = True
            if line[0] not in appended_noterm:
                grammar.append(Rule(NonTerm(line[0]),nullable, rules))
                appended_noterm.append(line[0])
                index_dict[line[0]] = len(grammar) - 1
            else:
                index = index_dict[line[0]]
                for elem in rules:
                    grammar[index].children.append(elem)
            line = f.readline().rstrip().split(' ->')
        return grammar, index_dict, nullable_list

def make_rule_better(elem):
    for i in range(len(elem.children)):
        buff = []
        open_par = 0
        buf_str = ""
        for symbol in elem.children[i]:
            if open_par == 0 and symbol != '[':
                buff.append(Term(symbol))
            elif symbol == '[':
                open_par = 1
            elif open_par == 1 and symbol != ']':
                buf_str += symbol
            elif symbol == ']':
                open_par = 0
                buff.append(NonTerm(buf_str))
                buf_str = ""
        elem.children[i] = buff
            

def anti_refal_changes(gram):
    new_gram = Grammar()
    new_gram.nonterm_elem_dict = {}
    for elem in gram:
        new_gram.nonterm_elem_dict[elem.value] = make_rule_better(elem)

def main():
    p = Parser('laba4/input.txt')
    gram, index_dict, nullable_list = p.parse()

    new_gram = anti_refal_changes(gram)

    print('____BEGIN GRAMMAR____')
    for elem in gram:
        print(elem.get_value(), elem.children[0][0].value)
    print('________________')

main()