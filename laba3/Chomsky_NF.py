import itertools
import numpy as np

class NonTerm():

    def __init__(self, value = None, rules = None, nullable = False):
        self.value = value
        self.rules = rules
        self.nullable = nullable

    def split_long_rules(self, grammar, index_dict):
        for i in range(len(self.rules)):
            #print(self.rules[i], '======')
            lis = [i for i, letter in enumerate(self.rules[i]) if letter == '[']
            #print(lis)
            if (len(lis) <= 1 and (self.rules[i].find(']') == len(self.rules[i]) -1 or self.rules[i].find('[') <= 0)) or (len(lis) > 1 and self.rules[i].find(']') + 1 == lis[1]):
                #print(self.rules[i], '======')
                continue
            rest = None
            if self.rules[i].find('[') == 0:
                rest = self.rules[i][self.rules[i].find(']')+1:]
            else:
                rest = self.rules[i][self.rules[i].find('['):]
            new_nonterm = '[' + self.value[1:2] + str(index_dict[self.value[1:2]]) + ']'
            index_dict[self.value[1:2]] += 1
            first_part = None
            if self.rules[i].find('[') == 0:
                first_part = self.rules[i][:self.rules[i].find(']')+1]
            else:
                first_part = self.rules[i][:self.rules[i].find('[')]
            self.rules[i] = first_part + new_nonterm 
            #index_dict[new_nonterm] = 1
            grammar.append(NonTerm(new_nonterm, [rest]))
            #print(new_nonterm, [rest], '+++')
            grammar[-1].split_long_rules(grammar, index_dict)

    def check_epsilon_in(self, grammar, nullable_list):
        begin_len = len(self.rules)
        for i in range(begin_len):
            if self.rules[i].find(']') == -1 or (self.rules[i].find(']') == len(self.rules[i]) -1 and self.rules[i].find('[') != 0):
                continue
            if self.rules[i][self.rules[i].find('['):self.rules[i].find(']')] in nullable_list and self.rules[i].find('[') == 0:
                self.rules.append(self.rules[i][self.rules[i].find(']')::])
            if self.rules[i][self.rules[i].find('['):self.rules[i].find(']')] in nullable_list and self.rules[i].find(']') == len(self.rules[i]) - 1:
                self.rules.append(self.rules[i][::self.rules[i].find('[')])

    def check_chain_in(self,grammar):
        for elem in self.rules:
            if elem == self.value:
                self.rules.remove(self.value) 
            if len(self.rules) == 0:
                grammar.remove(self)
                return
        begin_len = len(self.rules)      
        for i in range(begin_len):
            #print(self.rules[i])
            if self.rules[i].find('[') == 0 and self.rules[i].find(']') == len(self.rules[i]) - 1 and find_rule_using_nonterm(grammar, self.rules[i]):                                                           #self.rules[i] != '$' and find_rule_using_nonterm(grammar, self.rules[i]) and ((len(self.rules[i]) == 1 and self.rules[i] != '$')                                                                                                                            #or ('0' <= self.rules[i][1] <= '9')):
                adding_rules = find_rule_using_nonterm(grammar, self.rules[i])
                self.rules.remove(self.rules[i])
                for rule in adding_rules:
                    self.rules.append(rule)

    def final_change(self,grammar):
        #term = []
        for i,rule in enumerate(self.rules):
            lis = [i for i, letter in enumerate(rule) if letter == ']']
            if rule.find('[') > 0:
                new_nonterm = NonTerm('[G' + rule[:rule.find('[')] + ']', [str(rule[:rule.find('[')])])
                if new_nonterm.value not in [i.value for i in grammar]:
                    grammar.append(new_nonterm)
                new_rule = '[G' + rule[:rule.find('[')] + ']' + rule[rule.find('['):]
                self.rules[i] = new_rule
                #term.append(rule[:rule.find('[')])
            if rule.find(']') < len(rule) - 1 and rule.find(']') != -1 and len(lis) == 1:
                #term.append(rule[rule.find(']') + 1:])
                new_nonterm = NonTerm('[G' + rule[rule.find(']') + 1:] + ']', [str(rule[rule.find(']') + 1:])])
                if new_nonterm.value not in [i.value for i in grammar]:
                    grammar.append(new_nonterm)
                new_rule = rule[:rule.find(']')+1] + '[G' + rule[rule.find(']') + 1:] + ']' 
                self.rules[i] = new_rule
        

class Parser():
    
    def __init__(self, filename = None):
        self.filename = filename

    def parse(self):
        grammar = []
        index_dict = {}
        nullable_list = []
        f = open(self.filename, 'r')
        line = f.readline().split(' -> ')
        while line[0]: 
            index_dict[line[0][1:line[0].find(']')]] = 1
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
            grammar.append(NonTerm(line[0], rules, nullable))
            line = f.readline().rstrip().split(' ->')
        return grammar, index_dict, nullable_list

def find_rule_using_nonterm(gram, nonterm):
    for elem in gram:
        if elem.value == nonterm:
            return elem.rules
    return 0

def delete_long_rules(gram,index_dict):
    num = len(gram)
    for i in range(num):
        gram[i].split_long_rules(gram, index_dict)
    return gram

def delete_epsilon_rules(gram, nullable_list):
    for elem in gram:
        elem.check_epsilon_in(gram, nullable_list)
    if gram[0].value in nullable_list:
        gram = [NonTerm(gram[0].value[:gram[0].value.find(']')] + '0]', [gram[0].value, '$'])] + gram
    for i in range(1, len(gram)):
        if '$' in  gram[i].rules:
            gram[i].rules.remove('$')
    return gram

def delete_chain_rules(gram):
    for elem in gram:
        elem.check_chain_in(gram)
    return gram

def delete_empty_rules(gram):
    new_gram = []
    for elem in gram:
        if len(elem.rules) == 0:
            continue
        new_gram.append(elem)
    return new_gram 

def final_change(gram):
    for elem in gram:
        elem.final_change(gram)   
        
    return gram

def main():
    p = Parser('laba3/cfg.txt')
    gram, index_dict, nullable_list = p.parse()

    #print('____BEGIN GRAMMAR____')
    #for elem in gram:
    #    print(elem.value, elem.rules)
    #print('________________')

    gram = delete_long_rules(gram, index_dict)

    #print('____DELETED LONG____')
    #for elem in gram:
    #    print(elem.value, elem.rules)
    #print('________________')

    gram = delete_epsilon_rules(gram, nullable_list)

    #print('____DELETED EPSI____')
    #for elem in gram:
    #    print(elem.value, elem.rules)
    #print('________________')

    gram = delete_chain_rules(gram)

    #print('____DELETED CHAIN____')
    #for elem in gram:
    #    print(elem.value, elem.rules)
    #print('________________')

    gram = delete_empty_rules(gram)

    #print('____FINAL____')
    #for elem in gram:
    #    print(elem.value, elem.rules)
    #print('________________')

    gram = final_change(gram)

    #print('____FINAL FINAL____')
    #for elem in gram:
    #    print(elem.value, elem.rules)
    #print('________________')

    return gram

if __name__ == '__main__':
    main()