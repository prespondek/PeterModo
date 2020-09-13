#python

import lx
import sys
import time

fg = lx.eval("query layerservice layers ? main")

edge_index_list = []
poly_index_list = lx.eval("query layerservice polys ? selected")
try:
    edge_index_list = [tuple(sorted(eval(x))) for x in lx.eval("query layerservice edges ? selected")]
except:
    edge_index_list.append(tuple(sorted(eval(lx.eval("query layerservice edges ? selected")))))


lx.eval("select.typeFrom edge;vertex;polygon;item;pivot;center;ptag true")
lx.eval("select.ring")
ring_edges = [tuple(sorted(eval(x))) for x in lx.eval("query layerservice edges ? selected")]
ring_edge_set = set(ring_edges)
lx.eval("select.convert vertex")
vertex_index_list = lx.eval("query layerservice verts ? selected")

edge_list = [edge_index_list]
old_polys = []

while ring_edge_set:
    edge_polys = []
    for edge in edge_index_list:
        edge_polys.append(lx.eval("query layerservice edge.polylist ? " + str(edge).replace(' ','')))
    poly_verts = []
    if not old_polys:
        for poly in edge_polys:
            poly_verts.append(lx.eval("query layerservice poly.vertlist ? " + str(poly)))
        old_polys.extend(edge_polys)
    else:
        for polys in edge_polys:
            try:
                poly = set(polys).difference(old_polys).pop()
            except:
                break
            poly_verts.append(lx.eval("query layerservice poly.vertlist ? " + str(poly)))
            old_polys.append(poly)
    if not poly_verts:
        break
    poly_edges = []
    for verts in poly_verts:
        for i in range(0,len(verts)-1):
            poly_edges.append(tuple(sorted([verts[i],verts[i+1]])))
        poly_edges.append(tuple(sorted([verts[len(verts)-1],verts[0]])))
    poly_edges = set(poly_edges).difference(edge_index_list)
    edge_index_list = list(ring_edge_set.intersection(poly_edges))
    edge_list.append(edge_index_list)
    ring_edge_set = ring_edge_set.difference(poly_edges)

my_vmap = None
vmaps = lx.eval("query layerservice vmaps ? texture")
for vmap in lx.eval("query layerservice vmaps ? texture"):
    if lx.eval("query layerservice vmap.selected ? " + str(vmap)):
        my_vmap = vmap
        break
    
for edges in edge_list:
    lx.eval("select.drop edge")
    for edge in edges:
        lx.command("select.element", layer=fg, type="edge", mode="add", index=edge[0], index2=edge[1])
    lx.eval("uv.align Left Average")
