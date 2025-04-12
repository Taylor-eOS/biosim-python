import tkinter as tk
import random
import math
import ast
from itertools import combinations
from settings import SENSOR, NEURON, ACTION

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
        self.positions = layout_graph(self.nodes, self.edges, self.canvas_width, self.canvas_height)[0]
        self.node_to_edges = {node: [] for node in self.nodes}
        for edge in self.edges:
            a, b = edge
            self.node_to_edges[a].append(edge)
            self.node_to_edges[b].append(edge)
        self.edge_items = {}
        self.node_items = {}
        self.drag_data = {"node": None, "dx": 0, "dy": 0}
        self.type_colors = {SENSOR: "#fdd835", NEURON: "#64b5f6", ACTION: "#ef5350"}
        self.node_radius = 14
        self.setup_ui()

    def setup_ui(self):
        self.root = tk.Tk()
        self.root.title("Draggable Network Diagram")
        self.canvas = tk.Canvas(self.root, width=self.canvas_width, height=self.canvas_height, bg="white")
        self.canvas.pack()
        self.draw_edges()
        self.draw_nodes()
        self.canvas.tag_bind("draggable", "<ButtonPress-1>", self.on_node_press)
        self.canvas.tag_bind("draggable", "<B1-Motion>", self.on_node_motion)
        self.canvas.tag_bind("draggable", "<ButtonRelease-1>", self.on_node_release)
        self.root.mainloop()

    def draw_edges(self):
        for edge in self.edges:
            src, tgt = edge
            x1, y1 = self.positions[src]
            x2, y2 = self.positions[tgt]
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
            line_id = self.canvas.create_line(x1_adj, y1_adj, x2_adj, y2_adj, fill=color, width=thickness, arrow=tk.LAST, arrowshape=(12, 15, 5))
            label_x = (x1 + x2) / 2 + (-dy) * 0.01
            label_y = (y1 + y2) / 2 + dx * 0.01
            label_id = self.canvas.create_text(label_x, label_y, text=f"{weight:.2f}", font=("Arial", 8), fill=color)
            self.edge_items[edge] = {"line": line_id, "label": label_id}

    def draw_nodes(self):
        for node in self.nodes:
            x, y = self.positions[node]
            node_type, node_id = node
            fill_color = self.type_colors[node_type]
            oval_id = self.canvas.create_oval(x - self.node_radius, y - self.node_radius, x + self.node_radius, y + self.node_radius, fill=fill_color, outline="black", tags=("draggable",))
            text_id = self.canvas.create_text(x, y, text=str(node_id), font=("Arial", 9, "bold"), fill="black", tags=("draggable",))
            self.node_items[node] = (oval_id, text_id)
            self.canvas.itemconfig(oval_id, tags=("draggable", f"node_{node[0]}_{node[1]}"))
            self.canvas.itemconfig(text_id, tags=("draggable", f"node_{node[0]}_{node[1]}"))

    def on_node_press(self, event):
        item = self.canvas.find_withtag("current")
        if not item:
            return
        for node, (oval_id, text_id) in self.node_items.items():
            if item[0] == oval_id or item[0] == text_id:
                self.drag_data["node"] = node
                x, y = self.positions[node]
                self.drag_data["dx"] = x - event.x
                self.drag_data["dy"] = y - event.y
                break

    def on_node_motion(self, event):
        node = self.drag_data["node"]
        if node is None:
            return
        new_x = event.x + self.drag_data["dx"]
        new_y = event.y + self.drag_data["dy"]
        self.positions[node] = [new_x, new_y]
        oval_id, text_id = self.node_items[node]
        self.canvas.coords(oval_id, new_x - self.node_radius, new_y - self.node_radius, new_x + self.node_radius, new_y + self.node_radius)
        self.canvas.coords(text_id, new_x, new_y)
        self.update_edges_for_node(node)

    def on_node_release(self, event):
        self.drag_data["node"] = None

    def update_edges_for_node(self, node):
        for edge in self.node_to_edges[node]:
            src, tgt = edge
            x1, y1 = self.positions[src]
            x2, y2 = self.positions[tgt]
            dx, dy = x2 - x1, y2 - y1
            dist = math.hypot(dx, dy)
            if dist == 0:
                continue
            ux, uy = dx/dist, dy/dist
            x1_adj = x1 + ux * self.node_radius
            y1_adj = y1 + uy * self.node_radius
            x2_adj = x2 - ux * self.node_radius
            y2_adj = y2 - uy * self.node_radius
            line_id = self.edge_items[edge]["line"]
            self.canvas.coords(line_id, x1_adj, y1_adj, x2_adj, y2_adj)
            label_x = (x1 + x2) / 2 + (-dy) * 0.01
            label_y = (y1 + y2) / 2 + dx * 0.01
            label_id = self.edge_items[edge]["label"]
            self.canvas.coords(label_id, label_x, label_y)

def ccw(A, B, C):
    return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

def lines_intersect(a1, a2, b1, b2):
    return (ccw(a1, b1, b2) != ccw(a2, b1, b2) and ccw(a1, a2, b1) != ccw(a1, a2, b2))

def count_crossings(edges, positions):
    crossings = 0
    for (a, b), (c, d) in combinations(edges, 2):
        if {a, b} & {c, d}:
            continue
        if lines_intersect(positions[a], positions[b], positions[c], positions[d]):
            crossings += 1
    return crossings

def layout_graph(nodes, edges, width, height, iterations=50):
    margin = 50
    lane_x = {SENSOR: margin, NEURON: width // 2, ACTION: width - margin}
    lanes = {SENSOR: [], NEURON: [], ACTION: []}
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
                barycenter = sum(neighbor_orders)/len(neighbor_orders) if neighbor_orders else order[node]
                new_order.append((node, barycenter))
            new_order.sort(key=lambda tup: tup[1])
            lanes[lane] = [node for node, _ in new_order]
            for idx, node in enumerate(lanes[lane]):
                order[node] = idx
    positions = {}
    for lane in lanes:
        lane_nodes = lanes[lane]
        count = len(lane_nodes)
        spacing = (height - 2*margin)/(count - 1) if count > 1 else 0
        for i, node in enumerate(lane_nodes):
            x_jitter = random.uniform(-50, 50)
            y_jitter = random.uniform(-10, 10)
            x = lane_x[lane] + x_jitter
            y = margin + i * spacing + y_jitter
            positions[node] = [x, y]
    return positions, 0

def read_connections_from_file(filename):
    with open(filename, 'r') as file:
        content = file.read()
    neuron_start = content.find("Neuron connections: ") + len("Neuron connections: ")
    neuron_end = content.find("]", neuron_start) + 1
    neuron_connections = ast.literal_eval(content[neuron_start:neuron_end])
    action_start = content.find("Action connections: ") + len("Action connections: ")
    action_end = content.find("]", action_start) + 1
    action_connections = ast.literal_eval(content[action_start:action_end])
    return neuron_connections + action_connections

def main():
    test_connections = [
        (SENSOR, 0, NEURON, 0, 0.5),
        (SENSOR, 0, NEURON, 1, 0.5),
        (SENSOR, 2, NEURON, 0, 0.91),
        (SENSOR, 2, ACTION, 0, 0.19),
        (NEURON, 0, ACTION, 1, 0.36),
        (NEURON, 1, ACTION, 1, -0.18),
        (SENSOR, 1, ACTION, 1, -0.69)]
    #GraphApp(test_connections)

    #Read connections from file
    connections_from_file = read_connections_from_file("connections.txt")
    GraphApp(connections_from_file)

if __name__ == "__main__":
    main()

