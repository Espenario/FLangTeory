class NonTerm():

    def __init__(self, value = None):
        self.value = value

    def get_type(self):
        return 'N'

    def get_value(self):
        return f"[{self.value}]"

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

    def get_value(self):
        return self.value

class Grammar():

    def __init__(self, nonterm_elem_dict = None, term_list = None, term_list_values = None,start_symbol=None):
        self.nonterm_elem_dict = nonterm_elem_dict or {}
        self.term_list = term_list or []
        self.term_list_values = term_list_values or []
        self.start_symbol = start_symbol

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

def make_rule_better(elem,new_gram):
    for i in range(len(elem.children)):
        buff = []
        open_par = 0
        buf_str = ""
        for symbol in elem.children[i]:
            if open_par == 0 and symbol != '[':
                if symbol not in new_gram.term_list_values:
                    new_gram.term_list.append(Term(symbol))
                    new_gram.term_list_values.append(symbol)
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
    return elem
            

def anti_refal_changes(gram):
    new_gram = Grammar()
    new_gram.nonterm_elem_dict = {}
    for elem in gram:
        new_gram.nonterm_elem_dict[elem.value] = make_rule_better(elem,new_gram)
        #print(elem.value.value)
        if elem.value.value == '[S]':
            #print(elem.value)
            new_gram.start_symbol = elem.value
    new_gram.term_list = list(set(new_gram.term_list))
    return new_gram

def find_suitable_form(gram):
    suitable_nonterms_r = {}
    suitable_nonterms_l = {}
    non_terms_r = []
    non_terms_l = []
    for value, elem in gram.nonterm_elem_dict.items():
        flag_r = 1
        flag_l = 1
        for rule in elem.children:
            if len(rule) == 2 and rule[0].get_type() == 'T' and rule[1].get_type() == 'N':
                flag_l = 0
            elif len(rule) == 2 and rule[0].get_type() == 'N' and rule[1].get_type() == 'T':
                flag_r = 0
            elif len(rule) > 1 or rule[0].get_type() != 'T':
                flag_r = 0
                flag_l = 0
        if flag_r:
            suitable_nonterms_r[value] = elem
            non_terms_r.append(value.value)
        if flag_l:
            suitable_nonterms_l[value] = elem
            non_terms_l.append(value.value)
    return suitable_nonterms_r, suitable_nonterms_l,non_terms_r,non_terms_l

def check_if_nont_suitable(M_l, M_r,nont_l, nont_r):
    final_M_r = {}
    final_M_l = {}
    candidates = {}
    candidate_values = []
    for value, elem in M_l.items():
        flag_l = 1
        for rule in elem.children:
            if len(rule) == 2 and rule[0].get_value() not in nont_l:
                flag_l = 0
                break
        if flag_l and not elem.nullable:
            candidates[value] = elem
            candidate_values.append(value)
            final_M_l[value] = elem

    for value, elem in M_r.items():
        flag_r = 1
        for rule in elem.children:
            if len(rule) == 2 and rule[1].get_value() not in nont_r:
                #print(rule[1].value)
                flag_r = 0
                break
        if flag_r and not elem.nullable:
            candidates[value] = elem
            candidate_values.append(value)
            final_M_r[value] = elem
    return final_M_r, final_M_l, candidates, candidate_values

def find_candidates(gram):
    M_r, M_l,nont_r, nont_l = find_suitable_form(gram)
    #print(M_r, M_l)
    final_M_r, final_M_l, candidates, candidates_values = check_if_nont_suitable(M_l, M_r,nont_l, nont_r)
    #print(gram.term_list)
    #print(candidates_values)
    final_candidat_values = candidates_values + gram.term_list
    #print(final_candidat_values)
    return final_candidat_values, candidates

def get_first1_for_nont(candidates, candidates_values):
    #print(candidates)
    first1 = {}
    for elem in candidates_values:
        if elem.get_type() == 'T':
            first1[elem.get_value()] = elem.get_value()
    for key in candidates.keys():
        first1[key.value] = []
    for value, rule in candidates.items():
        for child in rule.children:
            if child[0].get_type() == 'N':
                first1[value.value].append(child[0])
            elif len(child) > 1:
                first1[value.value].append(child[1])
    for value, rule in candidates.items():
        for child in rule.children:
            if child[0].get_type() == 'N':
                first1[value.value] += first1[child[0].get_value()]
                first1[value.value] = list(set(first1[value.value]))
            elif len(child) > 1:
                first1[value.value] += first1[child[1].get_value()]
    print(first1)
    return first1

def get_follow1_for_nont(first1, candidates, candidates_values):
    follow1 = {}
    for key in candidates.keys():
        follow1[key.value] = []
    for value, rule in candidates.items():
        for child in rule.children:
            if child[0].get_type() == 'N' and len(child) > 1:
                #print(child[1].get_value())
                if child[0].get_value() not in follow1:
                    follow1[child[0].get_value()] = []
                if first1[child[1].get_value()] not in follow1[child[0].get_value()]:
                    follow1[child[0].get_value()].append(first1[child[1].get_value()])
            if len(child) > 1:
                #print(follow1[child[0].get_value()], follow1[value.value])
                follow1[child[0].get_value()] += follow1[value.value]

    for value, rule in candidates.items():
        for child in rule.children:
            if child[0].get_type() == 'N' and len(child) > 1:
                #print(child[0].get_value())
                if child[0].get_value() not in follow1:
                    follow1[child[0].get_value()] = []
                if first1[child[1].get_value()] not in follow1[child[0].get_value()]:
                    follow1[child[0].get_value()].append(first1[child[1].get_value()])
            if len(child) > 1:
                #print(child[0].get_value(),value.value )
                follow1[child[0].get_value()] += follow1[value.value]
                follow1[child[0].get_value()] = list(set(follow1[child[0].get_value()]))
    
    print(follow1)

    for key, value in follow1.items():
        for elem in value:
            pass
            #print(elem[0].get_value(), elem[1].get_value())



def main():
    p = Parser('laba4/input.txt')
    gram, index_dict, nullable_list = p.parse()

    gram = anti_refal_changes(gram)

    help = 0
    print('____BEGIN GRAMMAR____')
    for value, elem in gram.nonterm_elem_dict.items():
        help = value
        print(value.value, elem.children)
    print('________________')

    #print(gram.nonterm_elem_dict[help].children[1][1] in gram.nonterm_elem_dict)

    candidates_values, candidates = find_candidates(gram)

    first1 = get_first1_for_nont(candidates, candidates_values)
    follow1 = get_follow1_for_nont(first1, candidates, candidates_values)
 
main()