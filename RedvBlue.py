import igraph as ig
import random
import copy

def user():
    play = input("Type 1 to play, or 2 to observe...\n--> ")
    if play == "1":
        total_grn = int(input("How many greens in this simulation?\n--> "))
        return total_grn

num_greens = 20
num_edges = 4*num_greens

g = ig.Graph.Erdos_Renyi(n=num_greens, m=num_edges) # random graph

g.add_vertices(3)

g.vs[-3]['colour'] = 'grey'

g.vs[-2]['colour'] = 'red'
                                    # grey arent connected to any green nodes currently.... might not need to be
g.vs[-1]['colour'] = 'blue'

red_agent = g.vs[-2]
                                    # varibles to access either agent        
blue_agent = g.vs[-1]

grey_agent = g.vs[-3]

for i in range(len(g.vs)-3):
    g.vs[i]['colour'] = 'green'

# initialising attributes
for i in g.vs:
    if i['colour'] == 'green':
        i['opinion'] = random.choice([0, 1])
        i['uncertainty'] = random.uniform(0.0, 1.0)
        i['following'] = True                                       # every green starts off following red. 
    if i['colour'] == 'blue':
        i['energy'] = 100
    if i['colour'] == 'red':
        i['followers'] = num_greens             # might just get rid of this
    if i['colour'] == 'grey':
        i['count'] = 0
        i['loyalty'] = random.uniform(-1.0, 1.0)

def pick_neighbour(i):
    return random.choice(i.neighbors())

def green_talk(g):
    for i in g.vs:
        if i['colour'] == 'green':
            j = random.choice(i.neighbors())
            if i['opinion'] == j['opinion']:
                max = max_unc(i, j)
                if max == 1:
                    diff = i['uncertainty'] - j['uncertainty']
                    i['uncertainty'] = i['uncertainty'] - (diff*0.25)
                elif max == -1:
                    diff = j['uncertainty'] - i['uncertainty']
                    j['uncertainty'] = j['uncertainty'] - (diff*0.25)
            else:
                max = max_unc(i, j)
                if max == 1:
                    diff = i['uncertainty'] - j['uncertainty']
                    if diff > 0.5:          # maybe make 0.55??
                        i['opinion'] = opinion_change(i)
                        i['uncertainty'] = i['uncertainty'] - (diff*0.25)
                    else:
                        i['uncertainty'] = i['uncertainty'] - (diff*0.25) # ?????
                        j['uncertainty'] = j['uncertainty'] + (diff*0.25) # ?????
                elif max == -1:
                    diff = j['uncertainty'] - i['uncertainty']
                    if diff > 0.5:
                        j['opinion'] = opinion_change(j)
                        j['uncertainty'] = j['uncertainty'] - (diff*0.25)
                    else:
                        j['uncertainty'] = j['uncertainty'] - (diff*0.5) # ?????
                        i['uncertainty'] = i['uncertainty'] + (diff*0.25)
    #return g



def max_unc(i, j):
    if i['uncertainty'] > j['uncertainty']:
        return 1
    elif i['uncertainty'] < j['uncertainty']:
        return -1
    else:
        return 0

def opinion_change(node):
    if node['opinion'] == 0:
        return 1
    else:
        return 0

# message dictionaries full of uncertainties
red_msg = {1:0.1, 2:0.2, 3:0.3, 4:0.4} #, 5:0.5, 6:0.6, 7:0.7, 8:0.8, 9:0.9, 10:1.0}               # red increases uncertainty (+ve)
                                                                                                # not sure if this is the right idea.
blue_msg = {1:0.1, 2:0.2, 3:0.3, 4:0.4} #, 5:0.5, 6:0.6, 7:0.7, 8:0.8, 9:0.9, 10:1.0}              # changed to same as red.....

def red_talk(g, red_msg, move):
    msg = red_msg[move]
    for i in g.vs:
        if i['colour'] == 'green':
            if i['following'] == True:
                if i['opinion'] == 1:
                    unc, lost = red_1(msg, i)
                    if lost == True:
                        i['following'] = False
                    else:
                        i['uncertainty'] = unc
                        if i['uncertainty'] > 1.0:
                            i['uncertainty'] = 1.0
                else:
                    unc, lost = red_0(msg, i)
                    if lost == True:
                        i['following'] = False
                    else:
                        i['uncertainty'] = unc
                        if i['uncertainty'] < 0:
                            i['uncertainty'] = 0
    #return g

def red_0(msg, green):
    lost = False
    diff = msg + green['uncertainty']
    if diff > 1.5:                      # need to tweak this value
        lost = True
        return green['uncertainty'], lost
    else:
        return (green['uncertainty'] - 0.5*(msg)), lost # 0.1*

def red_1(msg, green):
    lost = False
    diff = green['uncertainty'] - msg
    if diff < -0.6:                    # need to tweak this value
        lost = True
        return green['uncertainty'], lost
    else:
        return (green['uncertainty'] + 0.5*(msg)), lost # 0.1*

def blue_talk(g, blue_msg, move, blue_agent, active = False):
    if active == True:
        return grey_talk(g, grey_msg, grey_agent)
    else:
        msg = blue_msg[move]
        for i in g.vs:
            if i['colour'] == 'green':
                if i['opinion'] == 1:
                    i['uncertainty'] = blue_1(msg, i)
                    if i['uncertainty'] < 0:
                        i['uncertainty'] = 0
                else:
                    i['uncertainty'] = blue_0(msg, i)
                    if i['uncertainty'] > 1.0:
                        i['uncertainty'] = 1.0
        #return g

def blue_0(msg, green):
    return (green['uncertainty'] + 0.5*(msg)) # 0.1*

def blue_1(msg, green):
    return (green['uncertainty'] - 0.5*(msg)) # 0.1*


# similar implementation to R/B msg, with only one potent msg
grey_msg = {1:1.0}

# determines if the grey agent is loyal, and applies the appropriate msg, at no cost
def grey_talk(g, grey_msg, grey_agent):
    if grey_agent['count'] <= 5:
        if grey_agent['loyalty'] >= 0:      # good agent
            for i in g.vs:
                if i['colour'] == 'green':
                    if i['opinion'] == 1:
                        i['uncertainty'] = blue_1(grey_msg[1], i)
                        if i['uncertainty'] < 0:
                            i['uncertainty'] = 0
                    else:
                        i['uncertainty'] = blue_0(grey_msg[1], i)
                        if i['uncertainty'] > 1.0:
                            i['uncertainty'] = 1.0        
        else:                # bad agent
            for i in g.vs:
                if i['colour'] == 'green':
                    if i['following'] == True:
                        if i['opinion'] == 1:
                            unc, lost = red_1(grey_msg[1], i)
                            i['uncertainty'] = unc
                            if i['uncertainty'] > 1.0:
                                i['uncertainty'] = 1.0
                        else:
                            unc, lost = red_0(grey_msg, i)
                            i['uncertainty'] = unc
                            if i['uncertainty'] < 0:
                                i['uncertainty'] = 0
    grey_agent['count'] += 1
    return g


def printGraph(g):
    for i in g.vs:
        print(i)

# def round(g):
#     green_talk(g)
#     red_talk(g, red_msg, move)
#     blue_talk(g, blue_msg, blue_agent, False) # last boolean for if grey activated or not....
#     # OR grey_talk based on user input
#     return g

def get_votes(g):
    voting = 0
    not_voting = 0
    for i in g.vs:
        if i['colour'] == 'green':
            if i['opinion'] == 1:
                voting += 1                     
            else:                              
                not_voting += 1               
    if voting > not_voting:                     
        winning = 'blue'
    elif voting < not_voting:
        winning = 'red'
    else:
        winning = 'neither'

    return voting, not_voting, winning

def blue_loss(blue_agent):
    if blue_agent['energy'] <= 0:
        print("GAME OVER, blue agent ran out of energy.")
        return True

def red_followers():
    total = 0
    for i in g.vs:
        if i['colour'] == 'green':
            if i['following']:
                total += 1
    return total

# debugging
def get_green_att():
    for i in g.vs:
        if i['colour'] == 'green':
            print("id: " + str(i.index) + ", colour: " + i['colour'] + ", opinion: " + str(i['opinion']) + ", uncertainty: " + str(i['uncertainty']) + ", following: " + str(i['following']))

def main():
    #play = user()
    clock = 0
    v, nv, winning = get_votes(g)
    print("BEFORE START OF SIMULATION\n" + winning + " is winning\n" + "blue has " + str(v) + " votes and red had " + str(nv) + " votes\n" + "blue has " + str(blue_agent['energy']) + " energy left and red has " + str(red_followers()) + " followers left\n")
    while clock < 25:
        #round(g)
        #minimax(g, True, 50, alpha, beta, eval_func_voting)
        green_talk(g)
        get_green_att()
        red_move = minimax(g, True, 5, -float("Inf"), float("Inf"), eval_func_voting)
        red_talk(g, red_msg, red_move)
        print("red msg: " + str(red_msg[red_move]))

        #print(blue_msg)
        #blue_move = int(input("Select your move 1-5:\n"))
        #blue_talk(g, blue_msg, blue_move, blue_agent, False)
        #print("blue msg: " + str(blue_msg[blue_move]))
        #energy_cost = 5*blue_msg[blue_move]
        #blue_agent['energy'] -= energy_cost

        blue_move = minimax(g, False, 5, -float("Inf"), float("Inf"), eval_func_voting) 
        blue_talk(g, blue_msg, blue_move, blue_agent, False)
        print("blue msg: " + str(blue_msg[blue_move]))
        energy_cost = 5*blue_msg[blue_move]
        blue_agent['energy'] -= energy_cost

        v, nv, winning = get_votes(g)
        print("Round " + str(clock) + ":\n" + winning + " is winning\n" + "blue has " + str(v) + " votes and red had " + str(nv) + " votes\n" + "blue has " + str(blue_agent['energy']) + " energy left and red has " + str(red_followers()) + " followers left\n")
        clock += 1
        if blue_loss(blue_agent):
            winning = 'red'
            break
            
    print(winning + " agent won")

#A better evaluation function would be to focus on combatting the uncertainty red is aiming to introduce, as maximum uncertainty is really their win condition.
def eval_func_uncertainty(graph):
    if blue_loss(blue_agent):
        return float("Inf")
    if red_followers(red_agent) == 0:
        return -float("Inf")

#an evaluation function that returns a value determining who is winning in a given state of the graph based on the difference in voting
def eval_func_voting(graph):
    if blue_loss(blue_agent):
        return float("Inf")
    if red_followers() == 0:
        return -float("Inf")
    v, nv, winning = get_votes(graph)
    return nv - v

#a function to run minimax on a given graph
def minimax(graph, is_maximizing, depth, alpha, beta, eval_func):       #green_talk needs to go in here at some point, currently just plays red_talk() then blue_talk()
    if depth == 0: # blue_loss(blue_agent) or 
        return eval_func(graph)
    if is_maximizing:
        best_value = -float("Inf")
        moves = red_msg
        best_move = moves[1]     # the msg dictionary start at '1'.... changed from '0'
        for move in moves:
            new_graph = copy.deepcopy(graph)
            red_talk(new_graph, red_msg, move)
            hypothetical_value = minimax(new_graph, False, depth - 1, -float("Inf"), float("Inf"), eval_func)    #[0] - removed
            if hypothetical_value > best_value:
                best_value = hypothetical_value
                best_move = move
                #print(best_value)
            alpha = max(alpha, best_value)
            if alpha >= beta:
                break
        return best_move
    else:
        best_value = float("Inf")
        moves = blue_msg
        best_move = moves[1]        # the msg dictionary start at '1'.... changed from '0'
        for move in moves:
            new_graph = copy.deepcopy(graph)
            blue_talk(new_graph, blue_msg, move, blue_agent) # need to add 'active' to here (grey agent), blue_talk() defualts to False.
            hypothetical_value = minimax(new_graph, True, depth - 1, -float("Inf"), float("Inf"), eval_func)    #[0] - removed  
            if hypothetical_value < best_value:
                best_value = hypothetical_value
                best_move = move
                #print(best_value)
            beta = min(beta, best_value)
            if alpha >= beta:
                break
        return best_move

def user_round(g, clock, turn_limit, alpha, beta):
    while not clock > turn_limit and not blue_loss(blue_agent):
        printGraph(g)
        moves = blue_msg
        print("Available moves: ", moves)
        choice = 100
        good_move = False
        while not good_move:
            choice = input("Select a move:\n")
            try:
                move = int(choice)
            except ValueError:
                continue
            if move in moves:
                good_move = True
            blue_talk(g, blue_msg, choice, blue_agent) # need to add 'active' to here (grey agent), blue_talk() defualts to False.
                                                      # check whether lue_talk needs to take move or choice...
           
            if not clock > turn_limit and not blue_loss(blue_agent):
                result = minimax(g, True, 50, -float("Inf"), float("Inf"), eval_func_voting)  
                print("Computer chose: ", result)
                red_talk(g, red_msg, result)

def ai_round(g, clock, turn_limit, alpha, beta):
    while not clock > turn_limit and not blue_loss(blue_agent):                 # Condence to while_not_over()?
        printGraph(g)
        blue_result = minimax(g, False, 50, -float("Inf"), float("Inf"), eval_func_voting)   
        #blue_talk(g, blue_msg, choice, blue_agent)          # need to change up blue talk so its a choice and not random
        
        if not clock > turn_limit and not blue_loss(blue_agent):                    
            red_result = minimax(g, True, 50, -float("Inf"), float("Inf"), eval_func_voting)   
            #red_talk(g, red_agent, result, red_agent)

# No consideration of the costs of their actions at the moment, next step to add this

main()

#printGraph(g)

color_dict = {"green": "green", "red": "red", "blue": "blue", "grey": "grey"}

# ig.plot(g, vertex_color=[color_dict[colour] for colour in g.vs["colour"]])
