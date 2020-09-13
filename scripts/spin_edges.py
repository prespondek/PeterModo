#python
# Author: Peter Respondek
# Title: Spin Edges
# Description: Works like spin quads but for edges

import lx

def error(titleString, errorString):
    lx.eval("dialog.setup error")
    lx.eval("dialog.title \"%s\"" % titleString)
    lx.eval("dialog.msg \"%s\"" % errorString)
    lx.eval("dialog.open")

selmode = lx.eval("query layerservice selmode ?")
mainlayer = lx.eval("query layerservice layers ? main")

if selmode != "edge":
    lx.eval("poly.spinQuads")
    sys.exit("LXe_SUCCESS")
    
else:
    polys = []
    selected_polys = lx.evalN("query layerservice polys ? selected")
    edges = lx.evalN("query layerservice edges ? selected")
    for edge in edges:
        if lx.eval("query layerservice edge.numPolys ? " + str(edge)) == 2:
            polys.append(lx.evalN("query layerservice edge.polyList ? " + str(edge)))
    if not polys:
        sys.exit("LXe_SUCCESS")
    for poly in polys:
        lx.eval("select.drop polygon")
        lx.eval("select.element " + str(mainlayer) + " polygon add " + str(poly[0]))
        lx.eval("select.element " + str(mainlayer) + " polygon add " + str(poly[1]))
        lx.eval("poly.spinQuads")
    lx.eval("select.drop polygon")
    for poly in selected_polys: 
        lx.eval("select.element " + str(mainlayer) + " polygon add " + str(poly))
    lx.eval("select.typeFrom edge")
