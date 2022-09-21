import igraph as ig

g = ig.Graph.Erdos_Renyi(n=20, m=70)

ig.plot(g)
