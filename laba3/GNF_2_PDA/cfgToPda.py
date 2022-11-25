import GNF_2_PDA.Grammar.grammarImport as Grammar
import GNF_2_PDA.Utils.constants as constant
from GNF_2_PDA.Automata.state import State
from GNF_2_PDA.Automata.transition import Transition

debug = False # debug mode, shows stack contents while parsing

class Automaton:
    def __init__(self, states, transitions):
        self.states = states
        self.transitions = transitions

    def toPda(self):
        trFunc = {}
        print("Transitions:")
        for t in self.transitions:
            if t.inputSymbol == "":
                t.inputSymbol = constant.LAMBDA
            key = (t.currState, t.inputSymbol, t.popSymbol)
            # make a new key in transition function if not found
            if (not key in trFunc.keys()):
                trFunc[key] = []
            trFunc[key].append((t.nextState, t.pushSymbols))
        trFunc = enumerate(trFunc.items())
        for i, (key, value) in trFunc:
            print(constant.DELTA + '(' + str(key[0]) + ',' 
            + key[1] + ',' + key[2] + ') = {', end="")
            targets = []
            for val in value:
                pushStr = ''.join(val[1])
                targets.append(
                    '(' + str(val[0]) + ',' + pushStr + ')'
                )
            print(str(', ').join(targets) + ' }')
        return trFunc
    
    def checkMembership(self, string):
        stack = []
        stack.append(constant.EPSILON)
        # find initial state
        for state in self.states:
            if (state.isInitial):
                currState = state
                break
        finishProcess, state = self.matchStr(string, currState, stack)
        t = (state.isFinal and finishProcess)
        return t

    # has exponential time complexity, but is useful for small strings |w| <= 50
    def matchStr(self, string, currState, stack):
        # print(currState)
        idx = stack.__len__() -1
        top = stack[idx]
        finishProcess = False
        # next character to be processed
        if len(string) > 0:
            inputSym = string[0]
        else: inputSym = constant.LAMBDA
        state = currState
        visited = False # checks if any moves are left to backtrack

        for tr in self.transitions:
            if tr.currState is currState and (tr.inputSymbol == inputSym or tr.inputSymbol == constant.LAMBDA) and (tr.popSymbol == top):
                # remove last element from stack (pop simulation)
                newStack = stack [:-1]
                # add the non-lambda transition push symbols to stack
                pushSymbols = tr.pushSymbols[:]
                pushSymbols.reverse()
                for sym in pushSymbols:
                    if sym == constant.LAMBDA:
                        continue
                    newStack.append(sym)
                if debug:
                    print(newStack)
                # don't truncate if input symbol was lambda
                if (tr.inputSymbol == constant.LAMBDA):
                    finishProcess, state = self.matchStr(string[:], tr.nextState, newStack)
                else:
                    finishProcess, state = self.matchStr(string[1:], tr.nextState, newStack)
                visited = True #mark path traversed
                if state.isFinal and finishProcess: break


        if not visited: 
            # mark string processing finished only if string is reduced to base size 0
            finishProcess = (len(string) == 0) 

        return finishProcess, state


def main():
    #path = input("Path for grammar: ").strip()
    states, transitions = Grammar.importGrammar('laba3/gnf.txt')
    
    pda = Automaton(states, transitions)
    res = pda.toPda()
    return res

if __name__ == "__main__":
    main()

