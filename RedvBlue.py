import igraph as ig
import random

num_greens = 20
num_edges = 4*num_greens

g = ig.Graph.Erdos_Renyi(n=num_greens, m=num_edges) # random graph

g.add_vertices(3)

g.vs[-3]['colour'] = 'grey'

g.vs[-2]['colour'] = 'red'
                                    # grey, red and blue nodes arent connected to any green nodes currently.... might not need to be
g.vs[-1]['colour'] = 'blue'

red_agent = g.vs[-2]
                                    # varibles to access either agent        
blue_agent = g.vs[-1]

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

for i in g.vs:
    if i['colour'] == 'green':
        g.add_edge(red_agent, i)
        g.add_edge(blue_agent, i)

for i in g.es:
    if i.target == red_agent.index or i.target == blue_agent.index:
        i['uncertainty'] = 0.5

def pick_neighbour(i):
    return random.choice(i.neighbors())


def green_talk(g):
    for i in g.vs:
        if i['colour'] == 'green':
            j = random.choice(i.neighbors())                             # picks a random connected node (neighbour)
            while j['colour'] != 'green':
                j = pick_neighbour(i)

            if i['uncertainty'] < j['uncertainty']:                      # now does an opinion change
                j['opinion'] = opinion_change(j)                         # flips the node with greater uncertainty
            if i['uncertainty'] > j['uncertainty']:
                i['opinion'] = opinion_change(i)                     


            diff = mod_uncertainty(i, j)                          
            if i['uncertainty'] > j['uncertainty']:
                j['uncertainty'] += diff
                i['uncertainty'] -= diff
                                                                    # right now just had a basic change in uncertainty
            if i['uncertainty'] < j['uncertainty']:                 
                i['uncertainty'] += diff                            # essentially brings the 2 uncertainties closer together
                j['uncertainty'] -= diff                            # will need to create a more complex equation later
    return g

def mod_uncertainty(i, j):
    return abs( (i['uncertainty'] - j['uncertainty']) / 5 )

def opinion_change(node):
    if node['opinion'] == 0:
        return 1
    else:
        return 0

# message dictionaries full of uncertainties
red_msg = {1:0.1, 2:0.2, 3:0.3, 4:0.4, 5:0.5, 6:0.6, 7:0.7, 8:0.8, 9:0.9, 10:1.0}               # red increases uncertainty (+ve)
                                                                                                # not sure if this is the right idea.
blue_msg = {1:-0.1, 2:-0.2, 3:-0.3, 4:-0.4, 5:-0.5, 6:-0.6, 7:-0.7, 8:-0.8, 9:-0.9, 10:-1.0}    # blue decreases uncertainty (-ve)

# need to implement loss of followers
def red_talk(g, red_msg, red_agent):                                    # need to think of how red will lose followers
    for i in g.vs:                                                      # possible way potency/uncertainty = %lose.
        if i['colour'] == 'green':                                      # highly potent/uncertain (1/0.1) evaluates to 10
            if i['following'] == False:                                 # unpotent/certain evaluates to 0.1
                continue                                                # if greater than or equal to 5 potent msg will put off the consumer
            msg = random.randint(1, 10)
            if i['following'] == True:
                i['uncertainty'] += red_msg[msg]
                if i['uncertainty'] > 1.0:
                    i['uncertainty'] = 1.0
                if i['uncertainty']/red_msg[msg] >= 5:                  #this just picks midpoint, will try to make more continuous
                    i['following'] = False
            else:                                               # just picks a message randomly
                i['uncertainty'] += red_msg[msg]
                if i['uncertainty'] > 1.0:
                    i['uncertainty'] = 1.0                      # caps the uncertainty at the maximum (1.0)
    return g

def blue_talk(g, blue_msg, blue_agent):
    msg = random.randint(1, 10)                        # just picks a message randomly
    energy_cost = 5*blue_msg[msg]
    if blue_agent['energy'] + energy_cost < 0:                      # arbitrary turn energy cost. Will not allow consecuptive potent msgs (100+[15*-1])x10 = -50. 
        #print("You do not have enough energy for that!")            # must use greys to capture max potency.
        return g
    else:
        blue_agent['energy'] += energy_cost
        for i in g.vs:
            if i['colour'] == 'green':
                msg = random.randint(1, 10)
                i['uncertainty'] += blue_msg[msg]                  
                if i['uncertainty'] < 0.0:                           # caps the uncertainty at the minimum (0.0)
                    i['uncertainty'] = 0.0
        return g

# similar implementation to R/B msg, with only one potent msg
grey_msg = {1:-1.0, 2:1.0}

# determines if the grey agent is loyal, and applies the appropriate msg, at no cost
def grey_talk(g, grey_msg):
    if i['count'] <= 10:
        if i['loyalty'] >= 0:
            for i in g.vs:
                if i['colour'] == 'green':
                    i['uncertainty'] += grey_msg[1]
                    if i['uncertainty'] < 0.0:
                        i['uncertainty'] = 0.0        
        if i['loyalty'] < 0:
            for i in g.vs:
                if i['colour'] == 'green':
                    i['uncertainty'] += grey_msg[2]
                    if i['uncertainty'] > 1.0:
                        i['uncertainty'] = 1.0 
    i['count'] += 1
    return g


def printGraph(g):
    for i in g.vs:
        print(i)

def round(g):
    green_talk(g)
    red_talk(g, red_msg, red_agent)
    blue_talk(g, blue_msg, blue_agent)
    # OR grey_talk based on user input
    return g

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
    if blue_agent['energy'] == 0:
        print("GAME OVER, blue agent ran out of energy.")
        return True

def red_followers():
    total = 0
    for i in g.vs:
        if i['colour'] == 'green':
            if i['following']:
                total += 1
    return total

def main():
    clock = 0
    v, nv, winning = get_votes(g)
    print("BEFORE START OF SIMULATION " + winning + " is winning\n" + "blue has " + str(v) + " votes and red had " + str(nv) + " votes\n" + "blue has " + str(blue_agent['energy']) + " energy left and red has " + str(red_followers()) + " followers left\n")
    while clock < 50:
        round(g)
        v, nv, winning = get_votes(g)
        print("Round " + str(clock) + ":\n" + winning + " is winning\n" + "blue has " + str(v) + " votes and red had " + str(nv) + " votes\n" + "blue has " + str(blue_agent['energy']) + " energy left and red has " + str(red_followers()) + " followers left\n")
        clock += 1
        if blue_loss(blue_agent):
            winning = 'red'
            break
            
    print(winning + " agent won")


#main()

#printGraph(g)

color_dict = {"green": "green", "red": "red", "blue": "blue", "grey": "grey"}

ig.plot(g, vertex_color=[color_dict[colour] for colour in g.vs["colour"]])