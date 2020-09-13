#python

import lx
import modoutil
import modouv

mainlayer = lx.eval("query layerservice layers ? main")

selected_polys = lx.eval("query layerservice polys ? selected")
lx.eval("select.expand")
expanded_polys = lx.eval("query layerservice polys ? selected")
lx.eval("select.drop polygon")
for poly in selected_polys:
    lx.command("select.element", layer=mainlayer, type="polygon", mode="add", index=poly)

lx.eval("select.boundary")
lx.eval("edge.split")

side_edges = modoutil.getBoundarySideFromPolys(set(selected_polys))
modoutil.peeler(side_edges)
modouv.alignUVToAxis()

lx.eval("select.drop polygon")
for poly in expanded_polys:
    lx.command("select.element", layer=mainlayer, type="polygon", mode="add", index=poly)
lx.eval("!!vert.merge auto")
