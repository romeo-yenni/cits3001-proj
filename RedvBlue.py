import igraph as ig
import random
import matplotlib.pyplot as plt

num_greens = 20
num_edges = 70

g = ig.Graph.Erdos_Renyi(n=num_greens, m=num_edges) # random graph

g.add_vertices(2)

g.vs[-2]['colour'] = 'red'
                                    # red and blue node arent connected to any green nodes currently.... might not need to be
g.vs[-1]['colour'] = 'blue'

for i in range(len(g.vs)-2):
    g.vs[i]['colour'] = 'green'

# initialising attributes
for i in g.vs:
    if i['colour'] == 'green':
        i['opinion'] = random.uniform(-1.0, 1.0)
        i['uncertainty'] = random.uniform(0.0, 1.0)
        i['following'] = True                                       # every green starts off following red. 
    if i['colour'] == 'blue':
        i['energy'] = 100
    if i['colour'] == 'red':
        i['followers'] = num_greens


def green_talk(g):
    for i in g.vs:
        if i['colour'] == 'green':
            j = random.choice(i.neighbors())
            diff = mod_uncertainty(i, j)                            # right now changing uncertainty but i think should be changing opinion.
            if i['uncertainty'] > j['uncertainty']:
                j['uncertainty'] += diff
                i['uncertainty'] -= diff
                                                                    # right now just had a basic change in uncertainty
            if i['uncertainty'] < j['uncertainty']:                 # picks a random connected node (neighbour)
                i['uncertainty'] += diff                            # essentially brings the 2 uncertainties closer together
                j['uncertainty'] -= diff                            # will need to create a more complex equation later
    return g

def mod_uncertainty(i, j):
    return abs( (i['uncertainty'] - j['uncertainty']) / 5 )


# message dictionaries full of uncertainties
red_msg = {1:0.1, 2:0.2, 3:0.3, 4:0.4, 5:0.5, 6:0.6, 7:0.7, 8:0.8, 9:0.9, 10:1.0}               # red increases uncertainty (+ve)
                                                                                                # not sure if this is the right idea.
blue_msg = {1:-0.1, 2:-0.2, 3:-0.3, 4:-0.4, 5:-0.5, 6:-0.6, 7:-0.7, 8:-0.8, 9:-0.9, 10:-1.0}    # blue decreases uncertainty (-ve)

# need to implement loss of followers
def red_talk(g, red_msg):                                           # need to think of how red will lose followers
    for i in g.vs:
        if i['colour'] == 'green':
            if i['following'] == True:
                msg = random.randint(1, 10)                        # just picks a message randomly
                i['uncertainty'] += red_msg[msg]
                if i['uncertainty'] > 1.0:
                    i['uncertainty'] = 1.0                          # caps the uncertainty at the maximum (1.0)
    return g

# need to implement loss of energy
def blue_talk(g, blue_msg):
    for i in g.vs:
        if i['colour'] == 'green':
            msg = random.randint(1, 10)                        # just picks a message randomly
            i['uncertainty'] += blue_msg[msg]
            if i['uncertainty'] < 0.0:
                i['uncertainty'] = 0.0                          # caps the uncertainty at the minimum (0.0)
    return g

def printGraph(g):
    for i in g.vs:
        print(i)

def round(g):
    green_talk(g)
    red_talk(g, red_msg)
    blue_talk(g, blue_msg)
    return g

def get_votes(g):
    voting = 0
    not_voting = 0
    for i in g.vs:
        if i['colour'] == 'green':
            if i['opinion'] > 0:
                voting += 1                     # needs to think about what happens if voting/not
            else:                               # are equal, right now if they are equal 
                not_voting += 1                 # red wins.
    if voting > not_voting:
        winning = 'blue'
    else:
        winning = 'red'

    return voting, not_voting, winning

def main():
    clock = 0
    while clock < 10:
        round(g)
        v, nv, winning = get_votes(g)
        print("after the round, " + winning + " is winning")
        print("after the round, " + winning + " is winning")
        clock += 1
    print(winning + " agent won")


main()

#printGraph(g)

color_dict = {"green": "green", "red": "red", "blue": "blue", "grey": "grey"}

#ig.plot(g, vertex_color=[color_dict[colour] for colour in g.vs["colour"]])
