#python

import lx

mainlayer = lx.eval("query layerservice layers ? main");
lx.eval("select.convert edge")
selected_edges = (eval(x) for x in lx.eval("query layerservice edges ? selected"))
lx.eval("tool.set edge.addPoint on")
lx.eval("tool.attr edge.addPoint middle true")
for edge in selected_edges:
     lx.eval("select.type edge")
     lx.eval("select.element " + str(mainlayer) + " edge set " + str(edge[0]) + " " + str(edge[1]))
     lx.eval("@edgeSliceorAddVert.pl")
