import REGEX_2_DFA.Regex2DFA as Regex2DFA
import CFG_2_GNF.cfg_main as cfg_main






def main():
    complement = Regex2DFA.regex2DFA()
    greibach_normalized_cfg, ordered_nonterminals = cfg_main.main()


if __name__ == '__main__':
    main()