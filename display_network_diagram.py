import tkinter as tk
import random
import math

SENSOR = 0
NEURON = 1
ACTION = 2

connections = [
    (SENSOR, 2, NEURON, 1, 0.94),
    (SENSOR, 2, NEURON, 0, 0.91),
    (SENSOR, 2, ACTION, 0, 0.19),
    (NEURON, 0, ACTION, 1, 0.36),
    (NEURON, 1, ACTION, 1, -0.78),
    (SENSOR, 1, ACTION, 1, -0.69)
]

def layout_graph(nodes, edges, width, height, iterations=100):
    area = width * height
    k = math.sqrt(area / len(nodes))
    eps = 0.001
    pos = {node: [random.uniform(0, width), random.uniform(0, height)] for node in nodes}
    for _ in range(iterations):
        disp = {node: [0, 0] for node in nodes}
        for v in nodes:
            for u in nodes:
                if u == v:
                    continue
                dx = pos[v][0] - pos[u][0]
                dy = pos[v][1] - pos[u][1]
                dist = math.sqrt(dx*dx + dy*dy) + eps
                force = k*k / dist
                disp[v][0] += (dx / dist) * force
                disp[v][1] += (dy / dist) * force
        for v, u in edges:
            dx = pos[v][0] - pos[u][0]
            dy = pos[v][1] - pos[u][1]
            dist = math.sqrt(dx*dx + dy*dy) + eps
            force = (dist*dist) / k
            delta_x = (dx / dist) * force
            delta_y = (dy / dist) * force
            disp[v][0] -= delta_x
            disp[v][1] -= delta_y
            disp[u][0] += delta_x
            disp[u][1] += delta_y
        for v in nodes:
            disp_len = math.sqrt(disp[v][0]**2 + disp[v][1]**2)
            if disp_len > 0:
                pos[v][0] += (disp[v][0] / disp_len) * min(disp_len, 5)
                pos[v][1] += (disp[v][1] / disp_len) * min(disp_len, 5)
            pos[v][0] = min(width-30, max(30, pos[v][0]))
            pos[v][1] = min(height-30, max(30, pos[v][1]))
    return pos

def draw_brain(conn_list, canvas_width=600, canvas_height=400):
    root = tk.Tk()
    root.title("Genome Brain Visualization")
    canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg="white")
    canvas.pack()
    
    nodes = set()
    edges = []
    weights = {}
    for s_type, s_id, t_type, t_id, weight in conn_list:
        src = (s_type, s_id)
        tgt = (t_type, t_id)
        nodes.add(src)
        nodes.add(tgt)
        edges.append((src, tgt))
        weights[(src, tgt)] = weight

    positions = layout_graph(nodes, edges, canvas_width, canvas_height)

    # Node colors by type
    type_colors = {
        SENSOR: "#fdd835",  # yellow
        NEURON: "#64b5f6",  # blue
        ACTION: "#ef5350"   # red
    }

    node_radius = 15

    # Draw edges first
    for (src, sink) in edges:
        x1, y1 = positions[src]
        x2, y2 = positions[sink]
        weight = weights[(src, sink)]

        # Adjust line endpoints to node edges
        dx, dy = x2 - x1, y2 - y1
        dist = math.hypot(dx, dy)
        if dist == 0:
            continue
        ux, uy = dx / dist, dy / dist
        x1_adj = x1 + ux * node_radius
        y1_adj = y1 + uy * node_radius
        x2_adj = x2 - ux * node_radius
        y2_adj = y2 - uy * node_radius

        # Style based on weight
        color = "black" if weight >= 0 else "gray"
        thickness = max(1, int(abs(weight) * 3))
        canvas.create_line(x1_adj, y1_adj, x2_adj, y2_adj,
                         fill=color, width=thickness,
                         arrow=tk.LAST, arrowshape=(12, 15, 5))

        # Label placement perpendicular to the line
        label_x = (x1 + x2) / 2 + (-dy) * 0.05
        label_y = (y1 + y2) / 2 + dx * 0.05
        canvas.create_text(label_x, label_y, text=f"{weight:.2f}",
                         font=("Arial", 8), fill="black")

    # Draw nodes on top of edges
    for node, (x, y) in positions.items():
        node_type, node_id = node
        color = type_colors.get(node_type, "gray")
        canvas.create_oval(x - node_radius, y - node_radius,
                          x + node_radius, y + node_radius,
                          fill=color, outline="black")
        canvas.create_text(x, y, text=str(node_id),
                         font=("Arial", 10, "bold"))

    root.mainloop()

if __name__ == "__main__":
    draw_brain(connections)
