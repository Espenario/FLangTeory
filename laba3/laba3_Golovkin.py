import Chomsky_NF as cnf
import REGEX_2_DFA.Regex2DFA as Regex2DFA
import CFG_2_GNF.cfg_main as cfg_main
import GNF_2_PDA.cfgToPda as gnf2pda
from pyformlang.cfg import CFG
from pyformlang.cfg.llone_parser import LLOneParser
from pyformlang.regular_expression import Regex
import copy
#import Greibach_NF as gnf
import json

class HomRule():

    def __init__(self, rule = None, value = None):
        self.rule = rule
        self.value = value

class RegData():

    def __init__(self, value = None):
        self.value = value
    
    def get(self):
        return self.value

    def set(self, value):
        self.value = value
      
class RegNode():

    def __init__(self, children = None, type = None, value = None):
        self.children = children
        self.type = type
        self.value = value
        self.set_value()

    def set_value(self, str=None):
        if self.type == 'Una':
            self.value = self.children[0].value
        if self.type == 'Alt' or self.type == 'Concat':
            buf = []
            for i in range(0,len(self.children)):
                if type(self.children[i].value) is not list:
                    buf.append(self.children[i].value)
                else:
                    for val in self.children[i].value:
                        buf.append(val)
            self.value = buf
        if self.type == 'Hom' and str is not None:
            self.value.set(str)
    
    def get_value(self):
        if self.type == 'Una':
            #buf = self.value[0].get()
            #print(buf,'==========')
            #for i in range(1,len(self.value)):
                #buf += self.value[i].get()
            return '(' + self.children[0].get_value() + ')*'
        if self.type == 'Alt':
            buf = self.children[0].get_value()
            for i in range(1,len(self.children)):
                buf += '|' + self.children[i].get_value()
            return buf
        if self.type == 'Concat':
            buf = self.children[0].get_value()
            for i in range(1,len(self.children)):
                buf +=  '.' + self.children[i].get_value()
            return buf
        if self.type == 'Hom':
            return self.value.get()

class Parser():

    def __init__(self, filename = None, hom_rule_list = None):
        self.filename = filename
        self.hom_rule_list = hom_rule_list

    def parse(self):
        f = open(self.filename, 'r')
        line = f.readline().rstrip()
        lines = []
        begin_node = None
        if line == 'Grammar:':
            empty_line = f.readline().rstrip()
            #parser_gram = cnf.Parser(f)
            gram_line = f.readline().rstrip()
            while gram_line:
                lines.append(gram_line)
                gram_line = f.readline().rstrip()
            #gram, index_dict, nullable_list = parser_gram.parse()
            #gram_to_gnf = gnf.Resolve(gram)
            #gram_in_gnf = gram_to_gnf.convert()
            #empty_line = f.readline().rstrip()
        line = f.readline().rstrip()
        if line == 'Homomorphism:':
            empty_line = f.readline().rstrip()
            self.hom_rule_list = self.parse_hom_rule(f)
        line = f.readline().rstrip()
        if line == 'Regex:':
            empty_line = f.readline().rstrip() 
            regex_line = f.readline().rstrip()  
            begin_node = self.parse_regex(regex_line)
        return begin_node, lines
        #self.display_regex_structure(begin_node)

    def display_regex_structure(self,regex_node):
        for child in regex_node.children:
            print(child.get_value(), child.type, child.children)
            print('------------')
            if type(child.children) != 'RegNode' and len(child.children) != 0:
                self.display_regex_structure(child)

    def parse_hom_rule(self, f):
        hom_rule_list = {}
        parts = f.readline().rstrip().split(' = ')
        while parts[0]:
            value = parts[1]
            rule = parts[0][2:-1]
            hom_rule_list[rule] = value
            parts = f.readline().rstrip().split(' = ')
            #print(parts, rule, value)
        return hom_rule_list

    def parse_regex(self,regex):
        alternatives = self.parse_alternatives(regex)
        #print(alternatives)
        children = []
        for alt in alternatives:
            children.append(self.parse_concat(alt))
        if len(alternatives) > 1:
            return RegNode(children, 'Alt')
        else: return children[0]

    def parse_alternatives(self, regex):
        open_par = 0
        close_par = 0
        begin_index = 0
        children = []
        end = len(regex) - 1
        for i in range(len(regex)):
            if ((i == 0 and not(regex[i+1].isalpha()) and regex[i] == '(')
                or (i != 0 and i != end and regex[i] == '(' and not(regex[i-1].isalpha()) and not(regex[i+1].isalpha()))
                or (i == end and not(regex[i-1].isalpha()) and regex[i] == '(')):
                open_par += 1
            if ((i == 0 and not(regex[i+1].isalpha()) and regex[i] == ')')
                or (i != 0 and i != end and regex[i] == ')' and not(regex[i-1].isalpha()) and not(regex[i+1].isalpha()))
                or (i == end and not(regex[i-1].isalpha()) and regex[i] == ')')):
                close_par += 1
            if regex[i] == '|' and open_par == close_par:
                children.append(regex[begin_index:i])
                begin_index = i + 1
        children.append(regex[begin_index: end+1])
        return children
    
    def find_hom_rule(self, rule):
        for elem in self.hom_rule_list:
            if elem.rule == rule:
                return True
        return False
        
    def parse_concat(self, regex):
        if regex[-1] == '*':
            regex = regex[1:-2]
            children = []
            children.append(self.parse_regex(regex))
            return RegNode(children, 'Una')
        if regex in self.hom_rule_list:
            return RegNode([],'Hom', RegData(regex))
        begin_index = 0
        children = []
        open_par = 0
        end = len(regex) - 1
        for i in range(len(regex) - 2):
            if ((i == 0 and not(regex[i+1].isalpha()) and regex[i] == '(')
                or (i != 0 and i != end and regex[i] == '(' and not(regex[i-1].isalpha()) and not(regex[i+1].isalpha()))
                or (i == end and not(regex[i-1].isalpha()) and regex[i] == '(')):
                if i != 0 and open_par == 0:
                    children.append(self.parse_regex(regex[begin_index:i]))
                begin_index = i
                open_par += 1
            if ((i == 0 and not(regex[i+1].isalpha()) and regex[i] == ')')
                or (i != 0 and i != end and regex[i] == ')' and not(regex[i-1].isalpha()) and not(regex[i+1].isalpha()))
                or (i == end and not(regex[i-1].isalpha()) and regex[i] == ')')):
                open_par -= 1
            if not(regex[i].isalpha()) and not(regex[i+1].isalpha()) and regex[i+1] != '*' and regex[i+2].isalpha() and open_par == 0:
                children.append(self.parse_regex(regex[begin_index:i+1]))
                begin_index = i + 1
                continue
            if not(regex[i].isalpha()) and not(regex[i+1].isalpha()) and regex[i+2].isalpha() and open_par == 0:
                children.append(self.parse_regex(regex[begin_index:i+2]))
                begin_index = i + 2
                continue
        #print(self.find_hom_rule(regex[begin_index:end+1]))
        children.append(self.parse_regex(regex[begin_index:end+1]))
        return RegNode(children, 'Concat')

def apply_homomorhism(regex, hom_rule_list):
    for child in regex.children:
        if type(child.children) != 'RegNode' and len(child.children) != 0:
                apply_homomorhism(child, hom_rule_list)
        else:
            child.set_value(hom_rule_list[child.get_value()])

def create_regex_file(regex,p,flag):
    regex.get_value()
    with open('laba3/begin_regex.txt', 'w') as outfile:
        outfile.write(str(len(p.hom_rule_list)) + '\n')
        if flag == 1:
            for elem in p.hom_rule_list.keys():
                outfile.write(p.hom_rule_list[elem] + '\n')
        else:
            for elem in p.hom_rule_list.keys():
                outfile.write(elem + '\n')
        outfile.write(regex.get_value() + '\n')
        if flag == 1:
            outfile.write('Norm')

def create_cfg_file(cfg):
    with open('laba3/cfg.txt', 'w') as outfile:
        for elem in cfg:
            outfile.write(elem + '\n')

def create_gnf_file(gnf, p):
    with open('laba3/gnf.txt', 'w') as outfile:
        outfile.write(gnf.start.symbol + '\n')
        outfile.write(','.join(p.hom_rule_list.values()) + '\n')
        for rule in gnf.rules:
            outfile.write(str(rule.left.symbol + '->' + ''.join([el.symbol for el in rule.right])).rstrip() + '\n')

def check_states(main_nonterm, rule,total):
    global new_grammar
    every_state = [i for i in range(1,total)]
    X1 = []
    X2 = []
    X3_for1 = []
    X3_for2 = []
    X3 = []
    non_term1 = rule[:rule.find(']')+1]
    #print(non_term1)
    for elem in new_grammar:
        #print(non_term1, elem[1], '+++++++')
        if elem.value[1] == non_term1 and elem.value[0] != total and elem.value[2] != total:
            X1.append(elem.value[0])
            X3_for1.append(elem.value[2])
    non_term2 = rule[rule.find(']')+1:]
    #print(non_term2)
    for elem in new_grammar:
        if elem.value[1] == non_term2 and elem.value[0] != total and elem.value[2] != total:
            X3_for2.append(elem.value[0])
            X2.append(elem.value[2])
    if len(X3_for1) > 0 and len(X3_for2) > 0:
        X3 = list(set(X3_for1) & set(X3_for2))
    elif len(X3_for1) > 0:
        X3 = list(set(X3_for1))
    elif len(X3_for2) > 0:
        X3 = list(set(X3_for2))
    if len(X1) == 0:
        X1 = every_state
    if len(X2) == 0:
        X2 = every_state
    if len(X3) == 0:
        X3 = every_state
    X1 = list(set(X1))
    X2 = list(set(X2))
    #print(main_nonterm , non_term1, non_term2,X1,X2, X3)
    for x1 in X1:
        for x2 in X2:
            for x3 in X3:
                new_grammar.append(HomRule([(x1, non_term1, x3), (x3, non_term2, x2)],(x1, main_nonterm, x2)))
    #print("++++++++++++++++")
    #for elem in new_grammar:
       # print(elem.value, elem.rule)
    #print("++++++++++++++++")
    #return gram
    #pass

def delete_useless_rules():
    new_gram = []
    rules = []
    for elem in new_grammar:
        m = 1
        for non_term in elem.rule:
            if non_term not in [i.value for i in new_grammar] and type(elem.rule) == list:
                m = 0
        if m == 1:
            for i in elem.rule:
                rules.append(i)
            new_gram.append(HomRule(elem.rule,elem.value))
    #print('ffffff-------------------')
    #for elem in new_gram:
        #print(elem.value, elem.rule)
    #print('ffffff-------------------')
    #print(rules)
    #for elem in new_gram:
    #    if elem.value not in rules:
    #        new_gram.remove(elem)
    return new_gram

new_grammar = []

def check_not_double_rule(rule):
    lis1 = [i for i, letter in enumerate(rule) if letter == ']']
    lis2 = [i for i, letter in enumerate(rule) if letter == '[']
    if len(lis1) == 2 and len(lis2) == 2:
        if rule[lis2[0]:lis1[0]] == rule[lis2[1]:lis1[1]]:
            return False
    return True

def final_delete(value, gram,total):
    check = 1
    inserted = []
    while check == 1:
        check = 0
        for line in value:
            every_state = [i for i in range(1,total)]
            X1 = every_state
            X2 = every_state
            X3 = every_state
            buf = [i.value for i in gram]
            for x1 in X1:
                for x2 in X2:
                    for x3 in X3:
                        if (x1, line.value, x3) in buf and (x1, line.value, x2) in buf and [(x1, line.value, x3), (x3, line.value, x2),(x1, line.value, x2)] not in inserted:
                            check = 1
                            gram.append(HomRule([(x1, line.value, x3), (x3, line.value, x2)],(x1, line.value, x2)))
                            inserted.append([(x1, line.value, x3), (x3, line.value, x2),(x1, line.value, x2)])
    #print('-------------------')
    #for elem in gram:
       # print(elem.value, elem.rule)
    #print('-------------------')
    new_gram = []
    rules = []
    for elem in gram:
        m = 1
        for non_term in elem.rule:
            if non_term not in [i.value for i in gram] and type(elem.rule) == list:
                m = 0
        if m == 1:
            new_gram.append(HomRule(elem.rule,elem.value))
    
            
    return new_gram


def perform_intersection_for_simple_automaton(dfa, cfg):
    global new_grammar
    new_grammar = []
    rest_gram = []
    check = 0
    total = len(dfa.states)
    for elem in cfg:
        #print(elem)
        check = 0
        for rule in elem.rules:
            if rule.find('[') == -1 and rule != '$':
                check = 1
                for state in dfa.states:
                    if state.id != total and state.transitions[rule] != total:
                        new_grammar.append(HomRule(rule,(state.id, elem.value, state.transitions[rule])))
            else:
                check = 2
        if check == 2:
            rest_gram.append(elem)
    #for key, value in new_grammar.items():
       # print(key, value)
    #print(rest_gram)
    double_rule_gram = []
    for elem in rest_gram:
        for rule in elem.rules:
            if check_not_double_rule(rule):
                check_states(elem.value, rule, len(dfa.states))
            else:
                double_rule_gram.append(HomRule( rule, elem.value))
    #print('Before____Delete')
    #for elem in new_grammar:
        #print(elem.value, elem.rule)
    #print('---------------')
    new_grammar = delete_useless_rules()
    #for elem in new_grammar:
        #print(elem.value, elem.rule)
    final_gram = final_delete(double_rule_gram, new_grammar,len(dfa.states))
    #for elem in final_gram:
        #print(elem.value, elem.rule)

def create_PSP_file(p):
    psp_gram = []
    hom_rule_list = list(p.hom_rule_list.keys())
    hom_rule_list.sort()
    #print(hom_rule_list)
    half = int(len(hom_rule_list) / 2)
    for i in range(half):
        psp_gram.append(hom_rule_list[i] + '[S]' + hom_rule_list[i + half])
    psp_gram.append('$')
    #print(psp_gram)
    with open('laba3/cfg.txt', 'w') as outfile:
        outfile.write('[S] -> ' + '|'.join(psp_gram) + '|[S][S]')

def get_start_symbol(cfg, n):
    if n == 0:
        return cfg[0].value
    for elem in cfg:
        if elem.value == f"[1S0{n}]":
            return elem.value

def produce_first_100_left_output(cfg,n):
    cfg_start_symbol = get_start_symbol(cfg,n)
    #print(cfg_start_symbol)
    gen_d = {}
    words = []
    for production in cfg:
            if production.value not in gen_d:
                gen_d[production.value] = [[]]
            if production.rules[0].find('[') != -1:    # len(production.body) == 2:
                lis2 = [i for i, letter in enumerate(production.rules[0]) if letter == '[']
                obj1 = str(production.rules[0][:production.rules[0].find(']')+1])     
                obj2 = str(production.rules[0][lis2[1]:])                                      #for obj in production.body:
                if obj1 not in gen_d:
                    gen_d[obj1] = [[]]
                if obj2 not in gen_d:
                    gen_d[obj2] = [[]]
        # To a single terminal
    for production in cfg:
        body = production.rules[0]
        if production.rules[0].find('[') == -1:
            if len(gen_d[production.value]) == 1:
                gen_d[production.value].append([])
            if body not in gen_d[production.value][-1]:
                gen_d[production.value][-1].append(body)
                words.append(body)
                #if production.value == cfg_start_symbol:
                    #return words
                   #print(body)
                    #yield body
    # Complete what is missing
    #print("------------")
   # print(gen_d)
    #print("------------")
    current_length = 2
    count = 0
    total_no_modification = 0
    while current_length <= 100:
        was_modified = False
        for gen in gen_d.values():
            if len(gen) != current_length:
                gen.append([])
        for production in cfg:
            body = production.rules
            if len(gen_d[production.value]) != current_length + 1:
                gen_d[production.value].append([""])
            if production.rules[0].find('[') == -1:
                continue
           # print(production.value, '_+_+_+_+_+_')
            for i in range(1, current_length):
                j = current_length - i
                lis2 = [i for i, letter in enumerate(production.rules[0]) if letter == '[']
                #print(gen_d[str(production.rules[0][:production.rules[0].find(']')+1])][i], "-=-=-=-=-=-=-=")
                #print(gen_d[str(production.rules[0][lis2[1]:])][j], '_+_+==-=_+_-==--')
                for left in gen_d[str(production.rules[0][:production.rules[0].find(']')+1])][i]:
                    for right in gen_d[str(production.rules[0][lis2[1]:])][j]:
                        new_word = left + right
                        #print(new_word, "=================")
                        if new_word not in gen_d[production.value][-1]:
                            #print(new_word, "=================")
                            if new_word not in words:
                                words.append(new_word)
                                count += 1
                            if count == 200:
                                #print('here')
                                return words
                            was_modified = True
                            gen_d[production.value][-1].append(new_word)
                            #words.append(new_word)
                            if production.value == cfg_start_symbol:
                                #print(new_word)
                                words.append(new_word)
                                #return words
                                #yield new_word
        if was_modified:
            total_no_modification = 0
        else:
            total_no_modification += 1
        current_length += 1
        if total_no_modification > current_length / 2:
            return words
    return words

def apply_homomorhism_to_gram(gram,p):
    cfg_in_lines = []
    for i in range(len(gram)):
        line = ""
        if type(gram[i].rule) != list:
            line = f"[{gram[i].value[0]}{gram[i].value[1][1:-1]}{gram[i].value[2]}] -> {p.hom_rule_list[gram[i].rule]}"
        else:
            line = f"[{gram[i].value[0]}{gram[i].value[1][1:-1]}{gram[i].value[2]}] -> [{gram[i].rule[0][0]}{gram[i].rule[0][1][1:-1]}{gram[i].rule[0][2]}][{gram[i].rule[1][0]}{gram[i].rule[1][1][1:-1]}{gram[i].rule[1][2]}]"
        cfg_in_lines.append(line)
    return cfg_in_lines

def grammar_to_lines(gram):
    cfg_in_lines = []
    for i in range(len(gram)):
        line = ""
        if type(gram[i].rule) != list:
            line = f"[{gram[i].value[0]}{gram[i].value[1][1:-1]}{gram[i].value[2]}] -> {gram[i].rule}"
        else:
            line = f"[{gram[i].value[0]}{gram[i].value[1][1:-1]}{gram[i].value[2]}] -> [{gram[i].rule[0][0]}{gram[i].rule[0][1][1:-1]}{gram[i].rule[0][2]}][{gram[i].rule[1][0]}{gram[i].rule[1][1][1:-1]}{gram[i].rule[1][2]}]"
        cfg_in_lines.append(line)
    return cfg_in_lines

def check_language_empty(gram):
    
    pass


    

def main():
    # 1 Task ---------------#
    p = Parser('test4.txt')
    regex, cfg = p.parse()
    regex1 = copy.deepcopy(regex)
    #p.display_regex_structure(regex)
    apply_homomorhism(regex, p.hom_rule_list)
    #p.display_regex_structure(regex)
    create_regex_file(regex, p,1)
    create_cfg_file(cfg)
    complement = Regex2DFA.regex2DFA('laba3/begin_regex.txt')
    for i in range(len(complement.states)):
        complement.states[i].final = not(complement.states[i].final)
    #greibach_normalized_cfg, ordered_nonterminals = cfg_main.main()
    #create_gnf_file(greibach_normalized_cfg,p)
    #print(','.join(p.hom_rule_list.values()),greibach_normalized_cfg.start.symbol)
    #pda = gnf2pda.main()
    gram_in_cnf = cnf.main()
    print(complement)
    #print(gram_in_cnf)
    #print(p.hom_rule_list)
    perform_intersection_for_simple_automaton(complement, gram_in_cnf)
    gram_first = new_grammar
    gram_first = grammar_to_lines(gram_first)
    create_cfg_file(gram_first)
    #print('____PSP____')
    first_gram_in_cnf = cnf.main()
    for elem in first_gram_in_cnf:
        print(elem.value, elem.rules)
    print('________________')
    check_language_empty(gram_first)

    # 2 Task ---------------#

    #cfg = CFG.from_text("""
    #"Var:[S0]" -> $ | "Ter:a" "Var:[S1]" | "Ter:d" "Var:[S2]" | "Var:[S]" "Var:[S]"
    #"Var:[S]" -> "Ter:a" "Var:[S1]" | "Ter:d" "Var:[S2]" | "Var:[S]" "Var:[S]"
    #"Var:[S1]" -> "Var:[S]" "Ter:b"
    #"Var:[S2]" -> "Var:[S]" "Ter:c"
    #""")
    #regexx = Regex("a (a | b)* b | d (d | c)* c")
    #cfg_inter = cfg.intersection(regexx)
    #print(cfg_inter.is_empty())  # False
    #print(cfg_inter.is_finite())  # True

    #new_grammar = []

    create_regex_file(regex1, p,0)

    #print(regex1.get_value())
    complement = Regex2DFA.regex2DFA('laba3/begin_regex.txt')
    create_PSP_file(p)
    psp_in_cnf = cnf.main()
    # Это один большой костыль, но алгоритм для автомата не мой, и он косячит, почему-то...
    print(complement)
    for state in complement.states:
        state.transitions[complement.alphabet[0]],state.transitions[complement.alphabet[1]] = state.transitions[complement.alphabet[1]],state.transitions[complement.alphabet[0]]
    print(complement)
    # Это один большой костыль, но алгоритм для автомата не мой, и он косячит, почему-то...
    #print('____PSP____')
    #for elem in psp_in_cnf:
       # print(elem.value, elem.rules)
    #print('________________')
    perform_intersection_for_simple_automaton(complement, psp_in_cnf) 
    cfg1 = apply_homomorhism_to_gram(new_grammar,p)
    #print(cfg1)
    create_cfg_file(cfg1)
    gram_in_cnf_after = cnf.main()
    create_cfg_file(cfg)
    gram_in_cnf_before = cnf.main()
    #print('____FINAL FINAL____')
    #for elem in gram_in_cnf_before:
        #print(elem.value, elem.rules)
    #print('________________')

    words_after = sorted(list(set(produce_first_100_left_output(gram_in_cnf_after,len(complement.states) - 1))))
    words_before = sorted(list(set(produce_first_100_left_output(gram_in_cnf_before,0))))
    #print(sorted(words_after, key = len))
   # print(sorted(words_before, key = len))
    words_after = sorted(words_before, key = len)[:100]
    words_before = sorted(words_after, key = len)[:100]
    res = list(set(words_before) & set(words_after))
    if len(res) == 100:
        print("Неточностей не найдено")
    else:
        error_elem = list(set(words_before) - set(words_after))[0]
        print("Контрпример", error_elem)

main()