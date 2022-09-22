import igraph as ig
import random

num_greens = 20
num_edges = 70

g = ig.Graph.Erdos_Renyi(n=num_greens, m=num_edges) # random graph

g.add_vertices(2)

g.vs[-2]['colour'] = 'red'
                                    # red and blue node arent connected to any green nodes currently
g.vs[-1]['colour'] = 'blue'

for i in range(len(g.vs)-2):
    g.vs[i]['colour'] = 'green'

for i in g.vs:
    if i['colour'] == 'green':
        i['opinion'] = random.uniform(-1.0, 1.0)
        i['uncertainty'] = random.uniform(0.0, 1.0)
    if i['colour'] == 'blue':
        i['energy'] = 100
    if i['colour'] == 'red':
        i['followers'] = num_greens

# message dictionaries
red_msg = {1:0.1, 2:0.2, 3:0.3, 4:0.4, 5:0.5, 6:0.6, 7:0.7, 8:0.8, 9:0.9, 10:1.0} # uncertainty??

blue_msg = {1:0.1, 2:0.2, 3:0.3, 4:0.4, 5:0.5, 6:0.6, 7:0.7, 8:0.8, 9:0.9, 10:1.0} # certainty??

def green_talk(g):
    for i in g.vs:
        if i['colour'] == 'green':
            j = random.choice(i.neighbors())
            diff = mod_uncertainty(i, j)
            if i['uncertainty'] > j['uncertainty']:
                j['uncertainty'] += diff
                i['uncertainty'] -= diff
                                                                    # right now just had a basic change in uncertainty
            if i['uncertainty'] < j['uncertainty']:                 # picks a random connected node (neighbour)
                i['uncertainty'] += diff                            # essentially brings the 2 uncertainties closer together
                j['uncertainty'] -= diff                            # will probably need to create a more complex equation later
    return g

def mod_uncertainty(i, j):
    return abs( (i['uncertainty'] - j['uncertainty']) / 5 )

green_talk(g)

#ig.plot(g)
