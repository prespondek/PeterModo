#python

# Author: Peter Respondek

# Description: python rewrite of Seneca Menard's cutPastePolysSelEdgeRows.pl.
# Gets around a modo crash by being far more strict about your selection

import lx

def error(titleString, errorString):
    lx.eval("dialog.setup error")
    lx.eval("dialog.title \"%s\"" % titleString)
    lx.eval("dialog.msg \"%s\"" % errorString)
    lx.eval("dialog.open")


mainlayer = lx.eval("query layerservice layers ? main");

if lx.eval("select.count polygon ?") == 0:
    sys.exit("LXe_ABORT")
lx.eval("!!select.type polygon")
lx.eval("!!select.cut")
lx.eval("!!select.drop polygon")
lx.eval("!!select.invert")
lx.eval("!!select.paste")
lx.eval("!!select.invert")

edge_list = []

polys = set(lx.eval("query layerservice polys ? selected"))
while polys:
    lx.eval("!!select.drop polygon")
    lx.eval("!!select.element " + str(mainlayer) + " polygon set " + str(polys.pop()))
    lx.eval("!!select.connect")
    current_polys = lx.eval("query layerservice polys ? selected")
    lx.eval("!!select.drop edge")
    lx.eval("!!select.type polygon")
    lx.eval("!!select.boundary")
    boundary_edges = set(eval(x) for x in lx.eval("query layerservice edges ? selected"))
    
    loop_edges = []
    while boundary_edges:
        boundary_edge = boundary_edges.pop()
        lx.eval("select.element " + str(mainlayer) + " edge set " + str(boundary_edge[0]) + " " + str(boundary_edge[1]))
        lx.eval("select.loop")
        loop_edges.append([eval(x) for x in lx.eval("query layerservice edges ? selected")])
        boundary_edges -= set(loop_edges[len(loop_edges) - 1])
        
    lx.out(len(loop_edges))
    lx.out(loop_edges)
    if len(loop_edges) > 2:
        error ("Bad Selection", "Polygon selection has holes")
        sys.exit("LXe_ABORT")
    if len(loop_edges) == 2:
        error ("Bad Selection", "You selection is a polygon loop")
        sys.exit("LXe_ABORT")
        
    edge_verts = set()
    for poly in current_polys:
        edge_verts = edge_verts.symmetric_difference(set(lx.eval("query layerservice poly.vertList ? " + str(poly))))
    if len(edge_verts) != 4:
        error ("Bad Selection", "Selection contains broken polygons loops or has polygons with more or less than four vertices. Quads only")
        sys.exit("LXe_ABORT")

    edge_vert = edge_verts.pop()
    shortest_edge_vert = 0
    steps = 0
    lx.eval("select.type vertex")
    while edge_verts:
        lx.eval("select.element " + str(mainlayer) + " vert set " + str(edge_vert))
        test_vert = edge_verts.pop()
        lx.eval("select.element " + str(mainlayer) + " vert add " + str(test_vert))
        lx.eval("select.between")
        current_steps = lx.eval("query layerservice vert.N ? selected")
        if current_steps < steps or steps == 0:
            steps = current_steps
            shortest_edge_vert = test_vert

    lx.eval("select.element " + str(mainlayer) + " vert set " + str(edge_vert))
    lx.eval("select.element " + str(mainlayer) + " vert add " + str(shortest_edge_vert))
    lx.eval("select.between")
    lx.eval("select.convert edge")
    if lx.eval("query layerservice edge.N ? selected") > 1:
        edge_list.extend([eval(x) for x in lx.eval("query layerservice edges ? selected")])
    else:
        edge_list.extend([eval(lx.eval("query layerservice edges ? selected"))])
    polys -= set(current_polys)

lx.eval("!!select.drop edge")
for edge in edge_list:
    lx.eval("select.element " + str(mainlayer) + " edge add " + str(edge[0]) + " " + str(edge[1]))
