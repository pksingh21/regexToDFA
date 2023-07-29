import graphviz as gv

globalLabelIndex = 0
globalStateIndex = 0
all_nfas = []
# define a class for representing the state of NFA


class NFA:
    # constructor
    def __init__(self, label=None, startState=None, finalState=None):
        self.startState = startState
        self.finalState = finalState
        self.multipleStartStates = [startState]
        self.multipleFinalStates = [finalState]
        self.transitions = {}
        self.label = label
        self.operationsDone = []

    def add_transition(self, startNode, endNode, edgeLabel):
        transition = NFATransition(startNode, endNode, edgeLabel)
        self.transitions[(startNode, endNode, edgeLabel)] = transition


class NFATransition:
    def __init__(self, startNode, EndNode, edgeLabel):
        self.startNode = startNode
        self.EndNode = EndNode
        self.edgeLabel = edgeLabel


def updateGlobalVariables():
    global globalStateIndex
    global globalLabelIndex
    globalStateIndex += 2
    globalLabelIndex += 1
    return globalStateIndex, globalLabelIndex


def getNewNFA(edgeLabel=None):
    stateIndex, labelIndex = updateGlobalVariables()
    nfa = NFA(labelIndex, stateIndex-1, stateIndex)
    if edgeLabel is not None:
        nfa.add_transition(stateIndex-1, stateIndex, edgeLabel)
    return nfa


def KleeneStar(nfa):
    newNFA = getNewNFA()
    nfa.add_transition(newNFA.startState, nfa.startState, 'e')
    nfa.add_transition(nfa.finalState, nfa.startState, 'e')
    nfa.add_transition(nfa.finalState, newNFA.finalState, 'e')
    nfa.add_transition(newNFA.startState, newNFA.finalState, 'e')
    # transfer the previous existing transitions to new nfa
    for transition in nfa.transitions:
        key = (transition[0], transition[1], transition[2])
        transitionx = nfa.transitions[key]
        newNFA.add_transition(transitionx.startNode,
                              transitionx.EndNode, transitionx.edgeLabel)
    # print("final NFA in KleeneStar")
    # visualiseNFA(newNFA)
    # print("*********************")
    return newNFA


def Union(nfa1, nfa2):
    # print("NFAs in union operator : ")
    # visualiseNFA(nfa1)
    # visualiseNFA(nfa2)
    newNFA = getNewNFA()
    newNFA.add_transition(newNFA.startState, nfa1.startState, 'e')
    newNFA.add_transition(newNFA.startState, nfa2.startState, 'e')
    newNFA.add_transition(nfa1.finalState, newNFA.finalState, 'e')
    newNFA.add_transition(nfa2.finalState, newNFA.finalState, 'e')
    # transfer the previous existing transitions to new nfa
    for transition in nfa1.transitions:
        key = (transition[0], transition[1], transition[2])
        transitionx = nfa1.transitions[key]
        newNFA.add_transition(transitionx.startNode,
                              transitionx.EndNode, transitionx.edgeLabel)
    for transition in nfa2.transitions:
        key = (transition[0], transition[1], transition[2])
        transitionx = nfa2.transitions[key]
        newNFA.add_transition(transitionx.startNode,
                              transitionx.EndNode, transitionx.edgeLabel)
    # print("NFA after union")
    # visualiseNFA(newNFA)
    # print("*********************")
    return newNFA


def Concatenation(nfa1, nfa2):
    nfa1.add_transition(nfa1.finalState, nfa2.startState, 'e')
    nfa1.finalState = nfa2.finalState
    # transfer the nfa2 transitions to nfa1
    for transition in nfa2.transitions:
        key = (transition[0], transition[1], transition[2])
        transitionx = nfa2.transitions[key]
        nfa1.add_transition(transitionx.startNode,
                            transitionx.EndNode, transitionx.edgeLabel)
    # print("NFA in concatenation")
    # visualiseNFA(nfa1)
    # print("*********************")
    return nfa1


def thompsonConstruction(regex, operator_precendence):
    stack = []
    for character in regex:
        if character not in operator_precendence:
            newNFA = getNewNFA(character)
            stack.append(newNFA)
            all_nfas.append(newNFA)
        else:
            if character == '*':
                nfa = stack.pop()
                nfa.operationsDone.append("*")
                stack.append(KleeneStar(nfa))
            elif character == '.':
                nfa2 = stack.pop()
                nfa1 = stack.pop()
                nfa1.operationsDone.append(f". with  + {nfa2.label}")
                stack.append(Concatenation(nfa1, nfa2))
            elif character == '|':
                nfa2 = stack.pop()
                nfa1 = stack.pop()
                nfa1.operationsDone.append(f"| with  + {nfa2.label}")
                stack.append(Union(nfa1, nfa2))
    return stack.pop()


def infix_to_postfix(infix_expression, operator_precendence):
    output_queue = []
    stack = []
    for character in infix_expression:
        if character not in operator_precendence:
            output_queue.append(character)
        else:
            # if the operator is ( then push it to stack
            if character == '(':
                stack.append(character)
            # if the operator is ) then pop all the operators from stack and append it to output queue until ( is found
            elif character == ')':
                while stack[-1] != '(':
                    output_queue.append(stack.pop())
                stack.pop()
            else:
                # check  if stack top has operator with higher or equal precedence then remove it from stack top and append it to output queue
                while len(stack) != 0 and stack[-1] in operator_precendence and operator_precendence[stack[-1]] >= operator_precendence[character]:
                    output_queue.append(stack.pop())
                stack.append(character)
    while len(stack) != 0:
        output_queue.append(stack.pop())
    return "".join(output_queue)


def shuntingYard(regex):
    # print(regex, "regex it got")
    operator_precedence = {"*": 50, ".": 40, "|": 30, "(": 0, ")": 100}
    return infix_to_postfix(regex, operator_precedence)


def visualiseNFA(nfa):
    print("digraph finite_state_machine {")
    print(nfa.startState, "start state for nfa")
    print(nfa.finalState, "final state for nfa")
    print(nfa.label, "label for nfa")
    for transition in nfa.transitions:
        key = (transition[0], transition[1], transition[2])
        transitionx = nfa.transitions[key]
        print(transitionx.startNode, "->", transitionx.EndNode,
              "[ label = \"" + transitionx.edgeLabel + "\" ];")
    for operations in nfa.operationsDone:
        print(operations)
    print("}")


finalStates = set()


def EpsilonClosure(nfa, currentState):
    # a function to find the epsilon closure of a state
    epsilonClosure = set()

    def FindEpsilonTransitions(state):
        if state == nfa.finalState:
            # print("final state found by", currentState, state)
            finalStates.add(currentState)
        epsilonClosure.add(state)
        for transition in nfa.transitions:
            key = (transition[0], transition[1], transition[2])
            transitionx = nfa.transitions[key]
            if transitionx.startNode == state and transitionx.edgeLabel == 'e' and transitionx.EndNode not in epsilonClosure:
                FindEpsilonTransitions(transitionx.EndNode)
    FindEpsilonTransitions(currentState)
    return epsilonClosure


def Move(nfa, currentState, character):
    # a function to find the move of a state
    move = set()
    for transition in nfa.transitions:
        key = (transition[0], transition[1], transition[2])
        transitionx = nfa.transitions[key]
        if transitionx.startNode == currentState and transitionx.edgeLabel == character:
            move.add(transitionx.EndNode)
    return move


def RemoveEpsilonFromNFA(nfa):
    # set of all states in nfa
    states = set()
    for transition in nfa.transitions:
        key = (transition[0], transition[1], transition[2])
        transitionx = nfa.transitions[key]
        states.add(transitionx.startNode)
        states.add(transitionx.EndNode)
    # set of all characters in nfa
    characters = set()
    for transition in nfa.transitions:
        key = (transition[0], transition[1], transition[2])
        transitionx = nfa.transitions[key]
        if transitionx.edgeLabel != 'e':
            characters.add(transitionx.edgeLabel)
    # initialise the new nfa
    newNFA = NFA()
    newNFA.startState = nfa.startState
    newNFA.finalState = nfa.finalState
    newNFA.label = nfa.label
    # create a map of epsilon closure of each state
    epsilonClosureMap = {}
    for state in states:
        epsilonClosureMap[state] = EpsilonClosure(nfa, state)
    # create a move of each state for each character
    moveMap = {}
    for state in states:
        for character in characters:
            moveMap[(state, character)] = Move(nfa, state, character)
    # remove all empty sets from move map
    moveMapV2 = {}
    epsilonClosureMapv2 = {}
    for state in epsilonClosureMap:
        if len(epsilonClosureMap[state]) != 0:
            epsilonClosureMapv2[state] = epsilonClosureMap[state]
    for move in moveMap:
        if len(moveMap[move]) != 0:
            moveMapV2[move] = moveMap[move]

    moveMap = moveMapV2
    epsilonClosureMapv2 = epsilonClosureMap
    # print("epsilon closure map", epsilonClosureMap)
    # print("move map", moveMap)
    # iterate through states
    finalClosureSet = {}
    for state in states:
        closure = epsilonClosureMap[state]
        for character in closure:
            closures = set()
            for transitionCharacter in characters:
                if (character, transitionCharacter) in moveMap:
                    moves = moveMap[(character, transitionCharacter)]
                    # print(moves, character, transitionCharacter,
                        #   "moves and character and transition character for it")
                    for move in moves:
                        ok = epsilonClosureMap[move]
                        closures = closures.union(ok)
                    finalClosureSet[(state, transitionCharacter)] = closures
                    # print(closures, state, transitionCharacter, "closure")
        # epsilonClosure
    NonEpislonNFA = NFA()
    NonEpislonNFA.startState = nfa.startState
    NonEpislonNFA.finalState = nfa.finalState
    NonEpislonNFA.multipleFinalStates = finalStates
    NonEpislonNFA.multipleStartStates = [nfa.startState]
    NonEpislonNFA.label = nfa.label
    finalTransitions = []
    for transition in finalClosureSet:
        # print(transition,finalClosureSet[transition],"transition")
        for f in finalClosureSet[transition]:
            # print(transition[0],f,transition[1],"NFA information")
            finalTransitions.append(NFATransition(
                transition[0], f, transition[1]))
    for finalTransition in finalTransitions:
        NonEpislonNFA.add_transition(
            finalTransition.startNode, finalTransition.EndNode, finalTransition.edgeLabel)
    # NonEpislonNFA.transitions = finalTransitions

    return NonEpislonNFA


def generate_graph(nfa):
    """Generates a graph of the given NFA."""
    graph = gv.Digraph(format="png")
    # graph.graph_attr['nodesep'] = '1.0'
    # graph.graph_attr['ranksep'] = '0.5'
    graph.attr("node", shape="circle")
    graph.node(str(nfa.startState), shape="doublecircle",
               color="green", label="start state")
    graph.node(str(nfa.finalState), shape="doublecircle",
               color="red", label="end state")
    for transition in nfa.transitions:
        key = (transition[0], transition[1], transition[2])
        transitionx = nfa.transitions[key]
        graph.edge(str(transitionx.startNode),
                   str(transitionx.EndNode), transitionx.edgeLabel)
    # make all graph nodes having final states as double circle
    for finalState in nfa.multipleFinalStates:
        # print(finalState, "final state", nfa.startState, "nfa start state")
        if str(finalState) != str(nfa.startState):
            graph.node(str(finalState), shape="doublecircle",
                       color="red", label="end state")
        else:
            graph.node(str(finalState), shape="doublecircle",
                       color="violet", label="start + end state")

    return graph


def nfaTodfa(nfa):
    # function to convert nfa to dfa
    nfa.startState = str(nfa.startState)
    nfa.finalState = str(nfa.finalState)
    states = set()
    transitionx = {}
    for transition in nfa.transitions:
        key = (transition[0], transition[1], transition[2])
        keyv2 = (str(transition[0]), str(transition[1]), transition[2])
        # nfa.transitions[keyv2] = nfa.transitions[key]
        transitionx[keyv2] = keyv2
        transitiony = nfa.transitions[key]
        states.add(str(transitiony.startNode))
        states.add(str(transitiony.EndNode))

    # nfa.transitions = transitionx
    for transitionxElems in transitionx:
        nfa.transitions[transitionxElems] = NFATransition(
            transitionxElems[0], transitionxElems[1], transitionxElems[2])
    dfaStates = set()
    dfaStates.add(str(nfa.startState))
    # set of all characters in nfa
    characters = set()
    for transition in nfa.transitions:
        key = (transition[0], transition[1], transition[2])
        transitionx = nfa.transitions[key]
        if transitionx.edgeLabel != 'e':
            characters.add(transitionx.edgeLabel)
    moveMap = {}
    for state in states:
        for character in characters:
            moveMap[(state, character)] = Move(nfa, state, character)
    # remove all empty sets from move map
    moveMapV2 = {}
    for move in moveMap:
        if len(moveMap[move]) != 0:
            moveMapV2[move] = moveMap[move]
    moveMap = moveMapV2
    # print("move map", moveMap)
    # print("states", states)
    # print("characters", characters)
    # print("nfa start state", nfa.startState)
    dfa = NFA()
    dfa.startState = nfa.startState
    dfa.label = nfa.label
    dfa.transitions = {}
    states = set()
    states.add(nfa.startState)
    # for character in characters:
    #     print(character, "character")
    #     if (nfa.startState, character) in moveMap:
    #         states.add(concatArrayToString(
    #             moveMap[(nfa.startState, character)]))
    # print(states, "first level states")
    listOfStates = list(states)
    visitedStates = {}
    visitedStates[listOfStates[0]] = True
    dfaMoveMap = {}
    for state in listOfStates:
        # print(state, "at this state")
        actualState = state.split(",")
        visitedStates[state] = True
        for character in characters:
            # print(character, "at this character")
            reachableStates = set()
            for actualStateElem in actualState:
                if (actualStateElem, character) in moveMap:
                    # print(moveMap[(actualStateElem, character)],
                    #   actualStateElem, character, "move map")
                    reachableStates = reachableStates.union(
                        moveMap[(actualStateElem, character)])
            # print(reachableStates)
            if len(reachableStates) != 0:
                dfaMoveMap[(state, character)] = reachableStates
            combinedString = concatArrayToString(reachableStates)
            # print(combinedString, "combined string for character : ",character," and state :",state)
            if combinedString not in visitedStates and len(combinedString):
                # print(combinedString, visitedStates, character,
                #   state, "this combined string was not there")
                visitedStates[combinedString] = True
                listOfStates.append(combinedString)
    # print(listOfStates)
    # print(dfaMoveMap)
    for moves in dfaMoveMap:
        dfa.add_transition(moves[0], concatArrayToString(
            dfaMoveMap[moves]), moves[1])
    final_dfa_states = set()
    for state in listOfStates:
        for finalState in nfa.multipleFinalStates:
            if str(finalState) in state:
                final_dfa_states.add(state)
    final_dfa_states = list(final_dfa_states)
    dfa.finalState = concatArrayToString(final_dfa_states[0])
    dfa.multipleFinalStates = final_dfa_states
    return dfa


def concatArrayToString(array):
    # function to concatenate array of number to string
    string = ""
    j = 0
    array = sorted(array)
    for i in array:
        if j != len(array)-1:
            string += str(i)+","
        else:
            string += str(i)
        j += 1
    return string


# Test the function
if __name__ == "__main__":
    regex = "a.b|(b|f)*.c.d"
    regex=input("please give input regex to render the png image supported operations \n . for conctatenation \n | for union \n * for kleene star \n example : a.b|(b|f)*.c.d \"e\" being reserved for epsilon transitions \n")
    # regex = "a.b|b*"
    # regex = "a*.(b.c)*"
    # regex = "(a|b)*"
    # finalRegex = r"a.b|b*"
    # randomRegexString = next(generate_string(finalRegex))
    # print(randomRegexString)
    operator_precedence = {"*": 50, ".": 40, "|": 30, "(": 0, ")": 100}
    postFixRegex = shuntingYard(regex)
    # print(postFixRegex)
    finalEpsilonNfa = thompsonConstruction(
        postFixRegex, operator_precedence)
    # print("final nfa")
    # visualiseNFA(finalEpsilonNfa)
    # print("*********************")
    graphEpsilonNFA = generate_graph(finalEpsilonNfa)
    graphEpsilonNFA.render("epsilonNFA")
    finalNFA = RemoveEpsilonFromNFA(finalEpsilonNfa)
    # visualiseNFA(finalNFA)
    FinalNFAgraph = generate_graph(finalNFA)
    FinalNFAgraph.render("finalNFA")
    # print("**********************************")
    dfa = nfaTodfa(finalNFA)
    # visualiseNFA(dfa)
    dfa_graph = generate_graph(dfa)
    dfa_graph.render("dfa")
