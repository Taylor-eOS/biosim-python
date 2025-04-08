import tkinter as tk
import random
import math
from itertools import combinations
from utils import SENSOR, NEURON, ACTION

def ccw(A, B, C):
    return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

def lines_intersect(a1, a2, b1, b2):
    return (ccw(a1, b1, b2) != ccw(a2, b1, b2) and 
            ccw(a1, a2, b1) != ccw(a1, a2, b2))

def count_crossings(edges, positions):
    crossings = 0
    edges = [(s, t) for s, t in edges]
    for (a, b), (c, d) in combinations(edges, 2):
        if a == c or a == d or b == c or b == d:
            continue  #Skip connected edges
        if lines_intersect(positions[a], positions[b], positions[c], positions[d]):
            crossings += 1
    return crossings

def layout_graph(nodes, edges, width, height, iterations=100):
    best_pos = None
    min_crossings = float('inf')
    
    #Try multiple configurations
    for attempt in range(10):
        area = width * height
        k = math.sqrt(area / len(nodes))
        eps = 0.001
        pos = {node: [random.uniform(50, width-50), random.uniform(50, height-50)] 
               for node in nodes}
        
        for _ in range(iterations):
            disp = {node: [0, 0] for node in nodes}
            
            #Node repulsion
            for v, u in combinations(nodes, 2):
                dx = pos[v][0] - pos[u][0]
                dy = pos[v][1] - pos[u][1]
                dist = math.hypot(dx, dy) + eps
                force = (k ** 2) / dist
                disp[v][0] += (dx / dist) * force
                disp[v][1] += (dy / dist) * force
                disp[u][0] -= (dx / dist) * force
                disp[u][1] -= (dy / dist) * force
            
            #Edge attraction
            for v, u in edges:
                dx = pos[v][0] - pos[u][0]
                dy = pos[v][1] - pos[u][1]
                dist = math.hypot(dx, dy) + eps
                force = (dist ** 2) / k
                delta_x = (dx / dist) * force
                delta_y = (dy / dist) * force
                disp[v][0] -= delta_x
                disp[v][1] -= delta_y
                disp[u][0] += delta_x
                disp[u][1] += delta_y
            
            #Avoid crossing lines
            edge_list = [(s, t) for s, t in edges]
            for i, (a, b) in enumerate(edge_list):
                for j, (c, d) in enumerate(edge_list[i+1:], i+1):
                    if {a, b} & {c, d}:
                        continue
                    if lines_intersect(pos[a], pos[b], pos[c], pos[d]):
                        mid1 = [(pos[a][0]+pos[b][0])/2, (pos[a][1]+pos[b][1])/2]
                        mid2 = [(pos[c][0]+pos[d][0])/2, (pos[c][1]+pos[d][1])/2]
                        dx = mid1[0] - mid2[0]
                        dy = mid1[1] - mid2[1]
                        dist = math.hypot(dx, dy) + eps
                        force = k * 2 / dist
                        
                        for node in [a, b]:
                            disp[node][0] += (dx / dist) * force
                            disp[node][1] += (dy / dist) * force
                        for node in [c, d]:
                            disp[node][0] -= (dx / dist) * force
                            disp[node][1] -= (dy / dist) * force
            
            #Update positions
            for node in nodes:
                dx, dy = disp[node]
                dist = math.hypot(dx, dy)
                if dist > 0:
                    scale = min(dist, 10) / dist
                    pos[node][0] += dx * scale
                    pos[node][1] += dy * scale
                
                #Keep within bounds
                pos[node][0] = max(30, min(width-30, pos[node][0]))
                pos[node][1] = max(30, min(height-30, pos[node][1]))
        
        #Evaluate this layout
        current_crossings = count_crossings(edges, pos)
        if current_crossings < min_crossings:
            min_crossings = current_crossings
            best_pos = pos
            if min_crossings == 0:
                break  #Found good layout
    
    return best_pos, min_crossings

def draw_brain(conn_list, canvas_width=800, canvas_height=600):
    root = tk.Tk()
    root.title("Network Diagram")
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
    positions, crossings = layout_graph(nodes, edges, canvas_width, canvas_height)

    type_colors = {
        SENSOR: "#fdd835", #yellow
        NEURON: "#64b5f6", #blue
        ACTION: "#ef5350"  #red
    }
    node_radius = 14
    
    #Draw edges first
    for (src, sink) in edges:
        x1, y1 = positions[src]
        x2, y2 = positions[sink]
        weight = weights[(src, sink)]
        
        #Adjust endpoints to node edges
        dx, dy = x2 - x1, y2 - y1
        dist = math.hypot(dx, dy)
        if dist == 0:
            continue
        ux, uy = dx / dist, dy / dist
        x1_adj = x1 + ux * node_radius
        y1_adj = y1 + uy * node_radius
        x2_adj = x2 - ux * node_radius
        y2_adj = y2 - uy * node_radius
        
        color = "black" if weight >= 0 else "gray"
        thickness = max(1, int(abs(weight) * 3))
        canvas.create_line(x1_adj, y1_adj, x2_adj, y2_adj,
                         fill=color, width=thickness,
                         arrow=tk.LAST, arrowshape=(12, 15, 5))
        
        #Label placement
        label_x = (x1 + x2)/2 + (-dy)*0.05
        label_y = (y1 + y2)/2 + dx*0.05
        weight_text = f"{weight:.2f}" if weight >= 0 else f"({weight:.2f})"
        canvas.create_text(label_x, label_y, text=weight_text, font=("Arial", 8), fill=color)

    #Draw nodes on top
    for node, (x, y) in positions.items():
        node_type, node_id = node
        color = type_colors[node_type]
        canvas.create_oval(x-node_radius, y-node_radius,
                          x+node_radius, y+node_radius,
                          fill=color, outline="black")
        canvas.create_text(x, y, text=str(node_id),
                         font=("Arial", 9, "bold"), fill="black")
    root.mainloop()

if __name__ == "__main__":
    connections = [
        (SENSOR, 0, NEURON, 0, 0.5),
        (SENSOR, 0, NEURON, 1, 0.5),
        (SENSOR, 2, NEURON, 1, 0.94),
        (SENSOR, 2, NEURON, 0, 0.91),
        (SENSOR, 2, ACTION, 0, 0.19),
        (NEURON, 0, ACTION, 1, 0.36),
        (NEURON, 1, ACTION, 1, -0.18),
        (SENSOR, 1, ACTION, 1, -0.69)]
    draw_brain(connections)
