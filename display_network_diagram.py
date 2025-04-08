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
        SENSOR: "#6baed6",   # blue
        NEURON: "#fd8d3c",   # orange
        ACTION: "#74c476"    # green
    }

    node_radius = 15
    for node, (x, y) in positions.items():
        node_type, node_id = node
        color = type_colors.get(node_type, "gray")
        canvas.create_oval(x - node_radius, y - node_radius, x + node_radius, y + node_radius, fill=color, outline="black")
        canvas.create_text(x, y, text=str(node_id), fill="black")

    for (src, sink) in edges:
        x1, y1 = positions[src]
        x2, y2 = positions[sink]
        weight = weights[(src, sink)]
        thickness = max(1, int(abs(weight) * 3))
        canvas.create_line(x1, y1, x2, y2, fill="black", width=thickness, arrow=tk.LAST)
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        canvas.create_text(mx, my, text=str(round(weight, 2)), font=("Arial", 8), fill="black")

    root.mainloop()

if __name__ == "__main__":
    draw_brain(connections)

