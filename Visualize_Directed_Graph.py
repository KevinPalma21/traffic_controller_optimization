#!/usr/bin/env python3

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import math

def visualize_directed_graph(csv_file):
    df = pd.read_csv(csv_file)
    G = nx.DiGraph()

    #Add nodes with attributes
    for _, row in df.iterrows():
        node_name = row["Node Name"]
        # Convert X/Y coords to float if needed
        x_coord = float(row["X coordinate"]) if not pd.isna(row["X coordinate"]) else None
        y_coord = float(row["Y coordinate"]) if not pd.isna(row["Y coordinate"]) else None

        G.add_node(
            node_name, 
            node_type=row["Node Type"],
            vehicle_direction=row["vehicle direction"],
            x=x_coord,
            y=y_coord
        )

    #Add edges (directed) from each Node Name to the neighbor columns
    for _, row in df.iterrows():
        node_name = row["Node Name"]
        neighbors = []
        # Collect neighbors from the relevant columns
        if not pd.isna(row["Neighbor Nodes"]) and str(row["Neighbor Nodes"]).strip():
            neighbors.append(str(row["Neighbor Nodes"]).strip())
        if not pd.isna(row["Neighbor Nodes2"]) and str(row["Neighbor Nodes2"]).strip():
            neighbors.append(str(row["Neighbor Nodes2"]).strip())

        for nbr in neighbors:
            G.add_edge(node_name, nbr)
    pos = {}
    for node, attrs in G.nodes(data=True):
        x_coord = attrs.get("x")
        y_coord = attrs.get("y")
        if x_coord is not None and y_coord is not None and not (math.isnan(x_coord) or math.isnan(y_coord)):
            pos[node] = (x_coord * 10, -y_coord * 10)
        else:
            pos[node] = None
    nodes_with_coords = {n: p for n, p in pos.items() if p is not None}
    nodes_no_coords = [n for n, p in pos.items() if p is None]
    color_map = {
        "Entry": "green",
        "Exit": "red",
        "Intermediate": "grey",
        "Middle": "blue",
        "Traffic_Controller": "yellow"
    }
    def get_node_color(node):
        node_type = G.nodes[node].get("node_type", "")
        return color_map.get(node_type, "gray")
    plt.figure(figsize=(20, 12))
    
    if nodes_no_coords:
        subG_no_coords = G.subgraph(nodes_no_coords)
        temp_pos = nx.spring_layout(subG_no_coords, k=2.0, seed=42)
        for n in subG_no_coords.nodes():
            pos[n] = temp_pos[n]

    #Draw nodes with color by node type
    node_colors = [get_node_color(n) for n in G.nodes()]
    nx.draw_networkx_nodes(
        G,
        pos=pos,
        node_color=node_colors,
        node_size=800
    )
    nx.draw_networkx_edges(G, pos=pos, arrows=True, arrowstyle='->', arrowsize=12)
    nx.draw_networkx_labels(G, pos=pos, font_size=8)
    plt.title("Directed Graph from CSV (Node Type Coloring)")
    plt.axis("off")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    csv_file_path = "Directed_Graph - Static.csv"
    visualize_directed_graph(csv_file_path)
