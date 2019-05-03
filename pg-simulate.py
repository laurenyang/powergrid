import matplotlib.pyplot as plt
import networkx as nx

# vertex: tuple of (name of unit, generation=+1/consumption=-1)

W = ("WindFarm", 1)
S = ("SolarFarm", 1)
D = ("Neighborhood", -1)
B = ("Battery", 1)
P = ("PowerPlant", 1)

def main():
  constructSimpleGrid()

def constructSimpleGrid():
	G = nx.MultiDiGraph()
	G.add_node(W)
	G.add_node(S)
	G.add_node(D)
	G.add_node(B)
	G.add_node(P)




	G.add_edge(W, B, weight=3)
	G.add_edge(S, B, weight=4)
	G.add_edge(S, D, weight=6)
	G.add_edge(W, D, weight=5)
	G.add_edge(B, D, weight=3)

	for u, v, keys, weight in G.edges(data='weight', keys=True):
		if weight is not None:
			print(u, "is connected to", v, "with distance", weight)
			
	# nx.draw_planar(G)
	nodes = nx.draw_networkx_nodes(G, pos=nx.spring_layout(G))
	p = pos=nx.spring_layout(G)
	print(p)
	edge_labels = nx.draw_networkx_edge_labels(G,  p)
	plt.show()
	# nodes = nx.draw_networkx_nodes(G, pos=nx.spring_layout(G))

if __name__ == '__main__':
	main()
