import tkinter as tk
from tkinter import ttk
import random
import math
import ast
from itertools import combinations
import settings

class GraphApp:
    def __init__(self, conn_list, canvas_width=1200, canvas_height=1000):
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.conn_list = conn_list
        self.nodes = set()
        self.edges = []
        self.weights = {}
        added_edges = set()
        for s_type, s_id, t_type, t_id, weight in conn_list:
            src = (s_type, s_id)
            tgt = (t_type, t_id)
            self.nodes.add(src)
            self.nodes.add(tgt)
            edge = (src, tgt)
            if edge not in added_edges:
                self.edges.append(edge)
                added_edges.add(edge)
            self.weights[edge] = weight
        self.type_colors = {settings.SENSOR: "#fdd835", settings.NEURON: "#64b5f6", settings.ACTION: "#ef5350"}
        self.node_radius = 14
        self.setup_ui()

    def setup_ui(self):
        self.root = tk.Tk()
        self.root.title("Draggable Network Diagram")
        notebook = ttk.Notebook(self.root)
        clusters = self.compute_clusters()
        valid_clusters = [c for c in clusters if self.cluster_has_sensor_and_action(c)]
        if not valid_clusters:
            label = tk.Label(self.root, text="No cluster with both sensor and action found.")
            label.pack()
        else:
            for i, cluster in enumerate(valid_clusters):
                frame = tk.Frame(notebook, width=self.canvas_width, height=self.canvas_height)
                frame.pack(fill="both", expand=True)
                notebook.add(frame, text=f"{i+1}")
                canvas = tk.Canvas(frame, width=self.canvas_width, height=self.canvas_height, bg="white")
                canvas.pack(fill="both", expand=True)
                self.draw_cluster(cluster, canvas)
            notebook.pack(fill="both", expand=True)
        self.root.mainloop()

    def compute_clusters(self):
        neuron_nodes = {node for node in self.nodes if node[0] == settings.NEURON}
        graph = {node: set() for node in neuron_nodes}
        for edge in self.edges:
            src, tgt = edge
            if src in neuron_nodes and tgt in neuron_nodes:
                graph[src].add(tgt)
                graph[tgt].add(src)
        visited = set()
        clusters = []
        for node in neuron_nodes:
            if node not in visited:
                comp = set()
                stack = [node]
                while stack:
                    n = stack.pop()
                    if n not in visited:
                        visited.add(n)
                        comp.add(n)
                        stack.extend(graph[n] - visited)
                for edge in self.edges:
                    src, tgt = edge
                    if src in comp and tgt[0] in (settings.SENSOR, settings.ACTION):
                        comp.add(tgt)
                    elif tgt in comp and src[0] in (settings.SENSOR, settings.ACTION):
                        comp.add(src)
                #Remove neurons that don’t eventually lead to an action.
                comp = prune_unused_neurons(comp, self.edges)
                clusters.append(comp)
        return clusters

    def cluster_has_sensor_and_action(self, cluster):
        node_types = {node[0] for node in cluster}
        return settings.SENSOR in node_types and settings.ACTION in node_types

    def draw_cluster(self, cluster, canvas):
        cluster_edges = [edge for edge in self.edges if edge[0] in cluster and edge[1] in cluster]
        positions, _ = layout_graph(cluster, cluster_edges, self.canvas_width, self.canvas_height)
        node_items = {}
        edge_items = {}
        node_to_edges = {node: [] for node in cluster}
        for edge in cluster_edges:
            a, b = edge
            node_to_edges[a].append(edge)
            node_to_edges[b].append(edge)
        for edge in cluster_edges:
            src, tgt = edge
            x1, y1 = positions[src]
            x2, y2 = positions[tgt]
            dx, dy = x2 - x1, y2 - y1
            dist = math.hypot(dx, dy)
            if dist == 0:
                continue
            ux, uy = dx/dist, dy/dist
            x1_adj = x1 + ux * self.node_radius
            y1_adj = y1 + uy * self.node_radius
            x2_adj = x2 - ux * self.node_radius
            y2_adj = y2 - uy * self.node_radius
            weight = self.weights[edge]
            color = "black" if weight >= 0 else "gray"
            thickness = max(1, int(abs(weight) * 3))
            line_id = canvas.create_line(x1_adj, y1_adj, x2_adj, y2_adj, fill=color,
                                         width=thickness, arrow=tk.LAST, arrowshape=(12, 15, 5))
            label_x = (x1 + x2) / 2 + (-dy) * 0.01
            label_y = (y1 + y2) / 2 + dx * 0.01
            label_id = canvas.create_text(label_x, label_y, text=f"{weight:.2f}",
                                           font=("Arial", 8), fill=color)
            edge_items[edge] = {"line": line_id, "label": label_id}
        for node in cluster:
            x, y = positions[node]
            n_type, n_id = node
            fill_color = self.type_colors[n_type]
            oval_id = canvas.create_oval(x - self.node_radius, y - self.node_radius,
                                         x + self.node_radius, y + self.node_radius,
                                         fill=fill_color, outline="black", tags=("draggable",))
            text_id = canvas.create_text(x, y, text=str(n_id), font=("Arial", 9, "bold"),
                                         fill="black", tags=("draggable",))
            node_items[node] = (oval_id, text_id)
            canvas.itemconfig(oval_id, tags=("draggable", f"node_{n_type}_{n_id}"))
            canvas.itemconfig(text_id, tags=("draggable", f"node_{n_type}_{n_id}"))
        drag_data = {"node": None, "dx": 0, "dy": 0}

        def on_node_press(event):
            item = canvas.find_withtag("current")
            if not item:
                return
            for node, (oval, text) in node_items.items():
                if item[0] in (oval, text):
                    drag_data["node"] = node
                    x, y = positions[node]
                    drag_data["dx"] = x - event.x
                    drag_data["dy"] = y - event.y
                    break

        def on_node_motion(event):
            node = drag_data["node"]
            if node is None:
                return
            new_x = event.x + drag_data["dx"]
            new_y = event.y + drag_data["dy"]
            positions[node] = [new_x, new_y]
            oval, text = node_items[node]
            canvas.coords(oval, new_x - self.node_radius, new_y - self.node_radius,
                          new_x + self.node_radius, new_y + self.node_radius)
            canvas.coords(text, new_x, new_y)
            for edge in node_to_edges[node]:
                src, tgt = edge
                x1, y1 = positions[src]
                x2, y2 = positions[tgt]
                dx, dy = x2 - x1, y2 - y1
                dist = math.hypot(dx, dy)
                if dist == 0:
                    continue
                ux, uy = dx/dist, dy/dist
                x1_adj = x1 + ux * self.node_radius
                y1_adj = y1 + uy * self.node_radius
                x2_adj = x2 - ux * self.node_radius
                y2_adj = y2 - uy * self.node_radius
                canvas.coords(edge_items[edge]["line"], x1_adj, y1_adj, x2_adj, y2_adj)
                label_x = (x1 + x2) / 2 + (-dy) * 0.01
                label_y = (y1 + y2) / 2 + dx * 0.01
                canvas.coords(edge_items[edge]["label"], label_x, label_y)

        def on_node_release(event):
            drag_data["node"] = None
        canvas.tag_bind("draggable", "<ButtonPress-1>", on_node_press)
        canvas.tag_bind("draggable", "<B1-Motion>", on_node_motion)
        canvas.tag_bind("draggable", "<ButtonRelease-1>", on_node_release)

def layout_graph(nodes, edges, width, height, iterations=50):
    margin = 50
    lane_x = {settings.SENSOR: margin, settings.ACTION: width - margin}
    lanes = {settings.SENSOR: [], settings.NEURON: [], settings.ACTION: []}
    for node in nodes:
        lanes[node[0]].append(node)
    for lane in lanes:
        lanes[lane].sort(key=lambda n: n[1])
    order = {}
    for lane in lanes:
        for idx, node in enumerate(lanes[lane]):
            order[node] = idx
    neighbor_map = {node: [] for node in nodes}
    for v, u in edges:
        if v in nodes and u in nodes:
            neighbor_map[v].append(u)
            neighbor_map[u].append(v)
    for _ in range(iterations):
        for lane in lanes:
            new_order = []
            for node in lanes[lane]:
                neighbor_orders = [order[n] for n in neighbor_map[node] if n[0] != lane]
                barycenter = sum(neighbor_orders) / len(neighbor_orders) if neighbor_orders else order[node]
                new_order.append((node, barycenter))
            new_order.sort(key=lambda tup: tup[1])
            lanes[lane] = [node for node, _ in new_order]
            for idx, node in enumerate(lanes[lane]):
                order[node] = idx
    positions = {}
    for lane in (settings.SENSOR, settings.ACTION):
        lane_nodes = lanes[lane]
        count = len(lane_nodes)
        spacing = (height - 2 * margin) / (count - 1) if count > 1 else 0
        for i, node in enumerate(lane_nodes):
            x_jitter = random.uniform(-30, 30)
            y_jitter = random.uniform(-10, 10)
            x = lane_x[lane] + x_jitter
            y = margin + i * spacing + y_jitter
            positions[node] = [x, y]
    neurons = lanes[settings.NEURON]
    if neurons:
        layer = {n: 0 for n in neurons}
        for edge in edges:
            src, tgt = edge
            if tgt in neurons and src[0] == settings.SENSOR:
                layer[tgt] = max(layer[tgt], 1)
        changed = True
        while changed:
            changed = False
            for src, tgt in edges:
                if src in neurons and tgt in neurons:
                    new_layer = layer[src] + 1
                    if new_layer > layer[tgt]:
                        layer[tgt] = new_layer
                        changed = True
        layers_group = {}
        for n in neurons:
            layers_group.setdefault(layer[n], []).append(n)
        max_layer = max(layers_group.keys()) if layers_group else 1
        col_spacing = (width * 0.7) / max_layer
        for l in layers_group:
            group = layers_group[l]
            x = width * 0.15 + l * col_spacing + random.uniform(-20, 20)
            used_y = set()
            for node in group:
                for _ in range(10):
                    y = random.uniform(margin, height - margin)
                    if all(abs(y - uy) > 10 for uy in used_y):
                        used_y.add(y)
                        break
                else:
                    y = random.uniform(margin, height - margin)
                positions[node] = [x, y]
    return positions, 0

def prune_unused_neurons(cluster, edges):
    outgoing = {}
    for edge in edges:
        src, tgt = edge
        if src in cluster and src[0] == settings.NEURON and tgt in cluster and (tgt[0] in (settings.NEURON, settings.ACTION)):
            outgoing.setdefault(src, []).append(tgt)
    valid = set()
    for src, targets in outgoing.items():
        for t in targets:
            if t[0] == settings.ACTION:
                valid.add(src)
                break
    changed = True
    while changed:
        changed = False
        for src, targets in outgoing.items():
            if src in valid:
                continue
            for t in targets:
                if t in valid or (t[0] == settings.ACTION):
                    valid.add(src)
                    changed = True
                    break
    pruned = set()
    for node in cluster:
        if node[0] == settings.NEURON:
            if node in valid:
                pruned.add(node)
        else:
            pruned.add(node)
    return pruned

def read_connections_from_file(filename):
    with open(filename, 'r') as file:
        for line in file:
            if line.startswith("Example genome for generation"):
                genome_start = line.find(":") + 1
                genome = ast.literal_eval(line[genome_start:].strip())
                return genome
    return []

def main():
    connections_from_file = read_connections_from_file("connections.txt")
    GraphApp(connections_from_file)

if __name__ == "__main__":
    main()

