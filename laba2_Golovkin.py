from copy import deepcopy
from numpy import *
import regex


class RegNode(object):

    def __init__(self,val,children = None,derr = None): 
        self.value = val
        self.children = children
        self.letters = []
        self.derr = derr
        #print("REG", val, "CH" ,self.children)

    def find_all_lett(self, node):
        if type(node.children) != list or len(node.children) == 0:
                if node.value != '$':
                    self.letters.append(node.value)
                return
        for child in node.children:
            self.find_all_lett(child)

    def show_letters(self):
        return self.letters
    
    def restructure_tree(self):
        if len(self.children) > 2:
            self.children[2].children

    
    def der(self,letter):
        if type(self.children) != list or len(self.children) == 0:
                if letter == self.value:             
                    self.derr = '$'
                else:
                    self.derr = 'null'
                #self.value = self.derr
                return
        #print(self.value)
        for child in self.children:
            child.der(letter)
        if type(self.children[0]) == ConNode:
            #print(self.children[0].derr,self.children[1].derr, self.value, '!!!!!!')
            if self.children[0].derr == '$' and self.children[1].derr != 'null' and self.children[1].derr != '$':
                #print("FFFFFFFFFFFF")
                self.derr = self.children[1].value + '|' + self.children[1].derr
            elif self.children[0].derr == '$' and (self.children[1].derr == 'null' or self.children[1].derr == '$'):
                self.derr = self.children[1].value
            elif self.children[0].derr == 'null' and self.children[1].derr != 'null' and self.children[1].derr != '$':
                self.derr = self.children[1].derr
            elif self.children[0].derr == 'null':
                self.derr = 'null'
            elif self.children[1].derr == 'null':
                self.derr = self.children[0].derr + self.children[1].value
            else:
                self.derr = self.children[0].derr + self.children[1].value + '|' + self.children[1].derr
            #self.children[1].value = self.children[1].derr
            #self.children[0].value = self.children[0].derr
            return

        if type(self.children[0]) == UnaNode:
            if self.children[0].derr == '$':
                self.derr = '(' + self.children[0].value + ')*'
            elif self.children[0].derr == 'null':
                self.derr = 'null'
           # elif self.children[0].derr[-1] != ')' and self.children[0].derr[0] != '(':
                #if self.value == '(aba)*':
                #    print(self.children[0].value, self.children[0].derr, '!!!')
                #self.derr = '(' + self.children[0].derr + ')' + self.value    #'(' + self.children[0].derr + ')' + self.value
            #self.children[0].value = self.children[0].derr
            else:
                self.derr = self.children[0].derr + self.value
            return

        if type(self.children[0]) == AltNode:
            if self.children[0].derr == 'null':
                self.derr = self.children[1].derr
            elif self.children[1].derr == 'null':
                self.derr = self.children[0].derr
            elif self.children[0].derr == 'null' and self.children[1].derr == 'null':
                self.derr = 'null'
            else:
                if self.children[0].derr == self.children[1].derr:
                    self.derr = self.children[0].derr
                else:
                    self.derr =  self.children[0].derr + '|' + self.children[1].derr
            #self.children[1].value = self.children[1].derr
            #self.children[0].value = self.children[0].derr
            return
            


 
class AltNode(RegNode):

    def __init__ (self, val,children = None):
        self.value = val
        self.children = children
        #print("ALT", val,"CH" ,self.children)

class ConNode(RegNode):

    def __init__ (self, val, children = None):
        self.value = val
        self.children = children
       # print("Con", val,"CH" ,self.children)

class UnaNode(RegNode): 

    def __init__ (self, val, children = None):
        self.value = val
        self.children = children
        #print("Una", val,"CH" ,self.children)


class RegexParser():

    def __init__(self, text=None):
        self.text = text
        self.text_begin = text
        self.children = []

    def check_data(self):
        self.text = self.text.replace(' ','')  # Убираем пробелы
        """Проверяем на запрещенные символы"""
        for symbol in self.text:
            if not(symbol.isalpha()) and not(symbol in '|)$(+*'):
                print("В регулярке обнаружена гадость")
                raise SystemExit
        """Проверяем на количество скобочек"""
        i = 0
        #print(self.text)
        for symbol in self.text:
            if symbol == '(':
                i += 1
            elif symbol == ')':
                i -= 1
        if i != 0:
            print("Косяк с количеством скобок")
            raise SystemExit
    
    def parse(self):
        self.children = []
        reg_children = []
        self_children = []
        self.check_data()
        #print(self.text)
        #self.delete_out_brac()
        #print(self.text, '11111')
        self.simplify_alt()
        self.split_alt()
        #print(self.text, '22222')
        self_children = self.children
        #print(self.children, "+++")
        if len(self_children) > 1:
            #print("))))))))))))")
            children = self.split_concat(self_children[0])
            #print(self.children, "=====")
            self.text = self_children[1]
            children_other = self.parse_una()
            #print(self.children, "____")
            reg_children.append(AltNode(self_children[0], children))
            reg_children.append(AltNode(self_children[1], children_other))
        else:
            #print("000000000000000")
            #print(self.children[0])
            reg_children = self.split_concat(self_children[0])
            #reg_children.append(AltNode(self.children[0], children))
        root = RegNode(self.text_begin, reg_children)
        #print(root, "___")
        return root
    
    def simplify_alt(self):
        j = 0
        index_begin = 0
        alt_children = []
        for i in range(len(self.text)):
            if self.text[i] == '(':
                j += 1
            if self.text[i] == ')':
                j -= 1
            if self.text[i] == '|' and j == 0:
                alt_children.append(self.text[index_begin:i])
                index_begin = i + 1
                #alt_children.append(self.text[i+1:])
            if i == len(self.text) - 1:
                alt_children.append(self.text[index_begin:i + 1])
        #print(alt_children, self.text, '!!!!!!!!!')
        res = sorted(set(alt_children))
        #print(res, '&&&&&&&&&&&&')
        text = ''
        for elem in res:
            text += elem + '|'
        #print(text[:-1], '!!!!!!!!!')
        #print(self.text, '&&&&&&&&&&&&')
        self.text = text[:-1]
        self.text_begin = text[:-1]

    def parse_una(self):
        self.children = []
        reg_children = []
        self_children = []
        self.check_data()
        #print(self.text, '++++')
        #self.delete_out_brac()
        #print(self.text, '+++')
        #if len(self.text) >137:
            #raise SystemExit
        self.split_alt()
        self_children = self.children
        #print(len(self.children), "+++")
        if len(self_children) > 1:
            children = self.split_concat(self_children[0])
            self.text = self_children[1]
            children_other = self.parse_una()
            reg_children.append(AltNode(self_children[0], children))
            reg_children.append(AltNode(self_children[1], children_other))
        else:
            #print(self.children[0])
            reg_children = self.split_concat(self_children[0])
            #reg_children.append(AltNode(self.children[0], children))
        return reg_children

    def split_alt(self):
        j = 0
        index_begin = 0
        for i in range(len(self.text)):
            if self.text[i] == '(':
                j += 1
            if self.text[i] == ')':
                j -= 1
            if self.text[i] == '|' and j == 0:
                self.children.append(self.text[index_begin:i])
                index_begin = i + 1
                self.children.append(self.text[i+1:])
                break
            if i == len(self.text) - 1:
                self.children.append(self.text[index_begin:i + 1])
    
    def delete_out_brac(self):
        if self.text[0] == '(' and self.text[-1] == ')':
            self.text = self.text[1:len(self.text)-1]
    
    def parse_concat(self, regex):
        #print(regex, '!!!!')
        con_children = []
        una_children = []
        if len(regex) == 1:
            return ConNode(regex[0])
        if regex[0].isalpha() and regex[1] != '*' and regex[1] != '+':
            con_children.append(ConNode(regex[0]))
            con_children.append(self.parse_concat(regex[1:]))
            return con_children
        if regex[0] == '(' and regex[-1] == ')':
            self.text = regex[1:-1]
            return self.parse_una()
        if regex[0].isalpha() and (regex[1] == '*' or regex[1] == '+'):
            buf = []
            if len(regex) > 2:
                buf = self.parse_concat(regex[2:])
            una_children.append(UnaNode(regex[0], buf))
            return una_children
        if regex[0] == '(' and (regex[-1] == '*' or regex[-1] == '+'):
            self.text = regex[1:len(regex) - 2]
            #print(self.text, "___________")
            una_children.append(UnaNode(regex[1:len(regex)-2], self.parse_una()))
            #print(una_children[0].value)
            return una_children

    def split_concat(self, regex):
        alt_children = []
        begin_index = 0
        con_children = []
        i = 0
        for j in range(len(regex)):
            if regex[j] == '(':
                i += 1
            if regex[j] == ')':
                i -= 1
            if i == 0 and j < len(regex) - 1 and ((regex[j].isalpha() and regex[j + 1].isalpha()) 
                                                or (regex[j].isalpha() and regex[j + 1] == '(') 
                                                or (regex[j] == ')' and regex[j + 1].isalpha()) 
                                                or (regex[j] == ')' and regex[j + 1] == '(') 
                                                or (regex[j] == '*' and (regex[j + 1].isalpha() or regex[j + 1] == '('))
                                                or (regex[j] == '+' and (regex[j + 1].isalpha() or regex[j + 1] == '('))) :
                #print(regex[begin_index:j+1])
                con_children = self.parse_concat(regex[begin_index:j+1])
                #if (j + 1) - begin_index > 1:
                alt_children.append(ConNode(regex[begin_index:j+1], con_children))
                begin_index = j + 1
                break
        #if (j + 1) - begin_index > 1 and begin_index != 0:
        if begin_index == 0:
            con_children = self.parse_concat(regex[begin_index:])
            return con_children
        con_children = self.split_concat(regex[begin_index:])
        alt_children.append(ConNode(regex[begin_index:], con_children))
        return alt_children

class Brzozovsky():

    def __init__(self, val = None,parser = None):
        self.regex = val
        self.states = []
        self.letters = []
        self.states_values = []
        self.parser = parser
       # print(self.regex)

    def calc_lett(self):
        self.regex.find_all_lett(self.regex)
        self.regex.letters = list(set(self.regex.letters))
        self.letters = self.regex.letters
        #print(self.regex.letters)

    def calculate_derr(self,letter = 'a'):
        self.regex.der(letter)
        #print(res)
    
    def set_derr(self,root):
        root.value = root.derr
        #root.derr = None
        if type(root.children) != list or len(root.children) == 0:
            #print(root.value)
            return
        for child in root.children:
            self.set_derr(child)

    def get_all_states(self,root):
        self.parser.text = root.value
        regex = self.parser.parse()
        #regex = deepcopy(root)
        #print(self.letters, root.derr, '=====')
        for letter in self.letters:
            #print(letter)
            #self.regex = deepcopy(regex)
            #print(root.value, "+++--+", letter)
            #regex = deepcopy(root)
            regex.der(letter)
            begin_regex = regex.derr
            #print(regex.derr, '++++',regex.value,letter )
            pars = RegexParser(begin_regex)
            regex1 = pars.parse()
            #print(regex1.value, '----')
            #print(regex.derr, "----", letter, root.value ,self.states_values)
            if regex1.value in self.states_values:
                #print(self.regex.derr, "____", letter)
                continue
            else:
                #self.regex.der(letter)
                #print(self.regex.derr, "++++", letter)
                #print(self.regex.value, "-----", letter)
                if regex.derr == 'null':
                    continue
                #print(self.regex.derr, "++++", letter)
                #self.set_derr(regex)
                ##print(regex1.value)
                #self.simplify_regex(regex1)
                #print(regex1.value)
                self.states.append(regex1)
                self.states_values.append(regex1.value)
                #print(self.regex.children[0].children[0].derr)
                #regex.value = regex.derr
                self.get_all_states(regex1)

    '''
    def simplify_regex(self, regex = None):
        if type(regex.children) != list or len(regex.children) == 0:
            return
        if type(regex.children[0]) == AltNode and regex.children[0].value == regex.children[1].value:
            print(regex.value, regex.children[0].value)
            regex.value = regex.children[0].value
            regex = regex.children[0]
            print("+++++++")
            print(regex.value, regex.children)
        if type(regex.children) != list or len(regex.children) == 0:
            return
        for child in regex.children:
            self.simplify_regex(child)
    '''

    def simlify(self):
        flat_list = []
        for sublist in self.states:
            for item in sublist:
                flat_list.append(item)
        self.states = list(set(flat_list))

    def reverse(self, root):
        if type(root.children) != list or len(root.children) == 0:
            return
        if type(root.children[0]) == AltNode:
            root.children[0], root.children[1] = root.children[1], root.children[0]
            #print(root.children[0].value, root.children[1].value)
            child1 = root.children[0].value
            child2 = root.children[1].value
            self.reverse(root.children[1])
            self.reverse(root.children[0])
            #print(root.value, '---')
            if child2[0] == '(' and child2[-1] == ')':
                root.value = root.children[0].value + '|' + '(' + root.children[1].value + ')'
            elif child1[0] == '(' and child1[-1] == ')':
                root.value = '(' + root.children[0].value + ')' + '|' + root.children[1].value
            elif root.value[0] == '(' and root.value[-1] == ')':
                root.value = '(' + root.children[0].value + '|' + root.children[1].value + ')'
            else: 
                root.value = root.children[0].value + '|' + root.children[1].value
            #print(root.value, '+++')
        if type(root.children[0]) == UnaNode:
            #print(root.value, '_____')
            self.reverse(root.children[0])
            root.value = '(' + root.children[0].value + ')' + root.value[-1]
        if type(root.children[0]) == ConNode:
            root.children[0], root.children[1] = root.children[1], root.children[0]
            self.reverse(root.children[1])
            self.reverse(root.children[0])
            child1 = root.children[0].value
            child2 = root.children[1].value
            #print(child1, child2)
            #if child2[0] == '(' and child2[-1] == ')':
             #   root.value = root.children[0].value + '(' + root.children[1].value + ')'
           # elif child1[0] == '(' and child1[-1] == ')':
              #  root.value = '(' + root.children[0].value + ')' + root.children[1].value
            #else: 
            root.value = root.children[0].value + root.children[1].value

def get_alts(state, alts):
    if type(state.children) != list or len(state.children) == 0:
            return
    if type(state.children[0]) != AltNode:
        alts.append(state)
        return
    if type(state.children[0].children) != list or len(state.children) == 0 or type(state.children[0].children[0]) != AltNode:
        alts.append(state.children[0])
    if type(state.children[1].children) != list or len(state.children) == 0 or type(state.children[1].children[0]) != AltNode:
        alts.append(state.children[1])
    get_alts(state.children[1], alts)
    get_alts(state.children[0], alts)

def check_alt(states, states_values, flag = 0):
    new_states = []
    new_states_values = []
    for state in states:
        if type(state.children) != list or len(state.children) == 0:
            new_states.append(state)
            new_states_values.append(state.value)
            continue
        alts = []
        if type(state.children[0]) == AltNode:
            get_alts(state,alts)
            for alt in alts:
                #if alt.value not in states_values and alt.value not in new_states_values:
                new_states.append(alt)
                new_states_values.append(alt.value)
            continue
        elif state.value not in new_states_values:
            new_states.append(state)
            new_states_values.append(state.value)
    if flag:
        return sorted(set(new_states_values))
    return (new_states)

def solution(regex):
    begin_regex = regex
    pars = RegexParser(begin_regex)
    root = pars.parse()
    #print(root)
    #print(root.children[0].value) 
    br = Brzozovsky(root, pars)
    #print(root.children[0].value)
    br.calc_lett()
    br.letters.sort()
    #print(root.letters)
    #root.der('b')
    #print(root.derr, 'kkkkkkkkkkkk')
    #br.calculate_derr()
    #print(root.derr)
    br.get_all_states(br.regex)
    br.states.append(root)
    br.states_values.append(root.value)
    #print(br.states)
    first_states = deepcopy(br.states)
    res_states = []
    br.states = []
    #print(root.children[0].value)
    #br.reverse(root)
    #print(root.value)
    first_states = check_alt(first_states, br.states_values)
    #print(first_states[0].value, first_states[1].value,'gggggggggggg' )
    for state in first_states:
        br.states = []
        br.states_values = []
        #print(state.value, '====')
        br.reverse(state)
        #print(state.value, '______')
        #print(br.states)
        br.get_all_states(state)
        #print(br.states)
        br.states.append(state)
        #print(br.states)
        res_states.append(list(set(br.states)))
    
    
    #print(res_states)
    br.states = res_states
    br.simlify()
    #print(br.states.value)
    res = []
    for state in br.states:
        #br.parser.text = state
        #br.parser.text_begin = state
       # root = br.parser.parse()
        #print(root.value, "+++")
        br.reverse(state)
        res.append(state)
        #print(br.reverse(root))
    #print(br.states)
    res_final = check_alt(set(res), br.states_values, 1)
    if '$' in res_final:
        res_final.remove('$')
    #print(res_final)
    for state in res_final:
        print(state)     
    
            

def main():
    f = open('test2.txt','r')
    str = f.readline().strip()
    index = 1
    while str:
        print(index, "------------------------")
        #print(str)
        solution(str)
        print(index, "------------------------")
        index += 1
        str = f.readline().strip()
main()