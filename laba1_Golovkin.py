
from operator import eq
import string
import numpy as np
from itertools import combinations

def GetGramm():
    dict = {}
    f = open('test.txt','r')
    str = f.readline().split(" = ")
    nonterms = "".join(str[1].split())
    str = f.readline().split(" = ")
    str = f.readline().split(" -> ")
    str[1] = "".join(str[1].split())
    while str[0]:
        str[1] = "".join(str[1].split())
        if dict.get(str[0]):
            m = dict.get(str[0])
            m += [str[1]]
            dict[str[0]] = m
        else:
            dict[str[0]] = [str[1]]
        str = f.readline().split(" -> ")
    return dict,nonterms

def CheckNonTerms(dict, item,extrEqClass, nonterms):
    pattern = ""
    for symbol in item:
        if symbol in dict.keys():
            pattern += "-"
        elif symbol in nonterms:
            extrEqClass.append(symbol)
            pattern += symbol
        else:
            pattern += symbol
    return pattern

def FillEqClasses(patdict, item, eqClasses, num):
    checkpat = patdict[item]
    for nonterm, pattern in patdict.items():
        if nonterm != item and set(checkpat) == set(pattern):
            eqClasses[item] = eqClasses.get(nonterm)
            return eqClasses, num
    eqClasses[item] = num
    num += 1
    return eqClasses, num

def SplitEqClass(dict,nonterms):
    extrEqClass = []
    unified = {}
    eqClasses = {}
    numeqclass = 0
    for nonterm, defi in dict.items():
        patternlist = []
        for elem in defi:
            patternlist.append(CheckNonTerms(dict, elem, extrEqClass,nonterms))
        unified[nonterm] = patternlist
        eqClasses, numeqclass = FillEqClasses(unified, nonterm, eqClasses, numeqclass)  
    return eqClasses, unified,numeqclass, extrEqClass

def MatchEqv(itemp, itemd, eqClass):
    for i in range(0, len(itemp)):
        if itemp[i] == '-':
            itemp = itemp[:i] + str(eqClass.get(itemd[i])) + itemp[i+1:]
    return itemp

def get_key(value, d):
    for k, v in d.items():
        if v == value:
            return k

def GetNewEqvClass(patterns, eqClass, dict, num):
    newpatterns = {}
    flag = False
    for nonterm, defi in dict.items():
        col = []
        for i in range(0, len(defi)):   
            col.append(MatchEqv(patterns.get(nonterm)[i],defi[i], eqClass))
        newpatterns[nonterm] = col
    iterlist = list(combinations(newpatterns.values(), 2))
    for item in iterlist:
        if (eqClass.get(get_key(item[0], newpatterns))) == (eqClass.get(get_key(item[1], newpatterns))) and set(item[0]) != set(item[1]):
            key = get_key(item[1], newpatterns)
            flag = True
            eqClass[key] = num
    return flag, eqClass

def DisplayEqClasses(eqClasses):
    for value in list(set(eqClasses.values())):
        print({k for k in eqClasses if eqClasses[k] == value})

def DisplayAnswer(dict, eqClasses):
    DisplayEqClasses(eqClasses)
    for nonterm, defi in dict.items():
        for item in defi:
            print(nonterm + " -> " + " ".join(item))

def PrepareAnswer(dict, eqClasses):
    DisplayEqClasses(eqClasses)
    checked = {}
    for nonterm, defi in dict.items():
        if checked.get(eqClasses.get(nonterm)) == None:
            checked[eqClasses.get(nonterm)] = 1
            for item in defi:
                print(nonterm + " -> ",end='')
                buf = {}
                for elem in item:
                    if buf.get(eqClasses.get(elem)):
                        elem = buf.get(eqClasses.get(elem))
                        print(elem,end= ' ')
                    elif eqClasses.get(elem) != None:
                        print(elem,end= ' ')
                        buf[eqClasses.get(elem)] = elem
                    else:
                        print(elem,end= ' ')
                print()    

def main():
    dict,nonterms = GetGramm()
    eqClasses, patterns,numeqclass, extrEqClass = SplitEqClass(dict,nonterms)
    sorted_keys = sorted(eqClasses, key=eqClasses.get) 
    eqClassessort = {}
    for w in sorted_keys:
        eqClassessort[w] = eqClasses[w]
    flag, eqClassessort = GetNewEqvClass(patterns, eqClassessort,dict,numeqclass)  
    numeqclass += 1 
    while flag:
       flag, eqClassessort = GetNewEqvClass(patterns, eqClassessort,dict,numeqclass)
       numeqclass += 1
    if len(list(set(eqClassessort.values()))) == len(eqClassessort.keys()):
        if extrEqClass:
            print(extrEqClass)
        DisplayAnswer(dict,eqClassessort)
    else:
        if extrEqClass:
            print(extrEqClass)
        PrepareAnswer(dict, eqClassessort)
 

main()