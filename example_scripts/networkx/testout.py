import networkx as nx
import matplotlib.pyplot as plt

G = nx.Graph()
#nodelist = [(1,2,3), (4,5,6),(7,8,9)]

#G.add_node((1,2,3))
#G.add_node((4,5,6))

G.add_edge((1,2,3),(4,5,6), distance = 4.5)
G.add_edge((4,5,6),(70,8,9), distance = 10)
G.add_edge((70,8,9), (10,5,9), distance = 50)
G.add_edge((1,2,3), (10,5,9), distance = 20)
G.add_edge((20,2,3), (10,5,9), distance = 15)
#G.add_nodes_from(nodelist)
#print G.nodes(data=True)
node_list = {}
cnt = 0
for n in G.nodes:
    node_list[cnt] = (n[0],n[1])
    cnt+=1
shortest_path =  nx.shortest_path(G, source = (20,2,3), target = (4,5,6), weight = "distance")
print shortest_path
T = nx.minimum_spanning_tree(G)
edges = T.edges
print type(edges)
for e in edges:
    print e[0]
nx.draw(T, with_labels=True)
#nx.draw_networkx_labels(G,pos=node_list)
#nx.draw_networkx_nodes(G,node_list, node_size  = 10)
#nx.draw_networkx_edges(G,node_list,width=1.0,alpha=0.5)
plt.show()
'''
nshortpath = len(shortest_path)
total_distance = 0
for scnt in range(nshortpath):
    if scnt != nshortpath-1:
        network_edge = G[shortest_path[scnt]][shortest_path[scnt+1]]
        total_distance = total_distance + network_edge["distance"]
        print network_edge["distance"]
        print network_edge
    
print total_distance
nx.draw(G)
plt.show()
'''