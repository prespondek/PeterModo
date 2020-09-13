# python
# Author: Peter Respondek 
# Title: Merge Vertices
# Description: Merges vertices while trying to avoid making manifold geometry

import lx

threshold = None

args = lx.args()

for arg in args:
    try:
        threshold = float(arg)
    except:
        error("Invalid Number","This script takes floating point numbers only")
        sys.exit("LXe_INVALIDARG")
    

layer = lx.eval("query layerservice layers ? main")
selmode = lx.eval("query layerservice selmode ?")

lx.eval("select.convert vertex")
selected_verts = set(lx.evalN("query layerservice verts ? selected"))
if not selected_verts:
    lx.eval("select.all")
    selected_verts = set(lx.evalN("query layerservice verts ? selected"))
lx.eval("select.drop vertex")
lx.eval("select.edge add bond equal (none)")
lx.eval("select.convert vertex")
open_verts = set(lx.evalN("query layerservice verts ? selected"))
if not open_verts:
    lx.eval("select.typeFrom " + selmode)
    sys.exit()
lx.eval("select.drop vertex")
target_verts = set.intersection(selected_verts, open_verts)
for vert in target_verts:
    lx.command("select.element", layer=str(layer), type="vertex", mode="add", index=vert)  
if threshold:
    lx.eval("!!vert.merge fixed false " + threshold + " morph:false disco:false")
else:
    lx.eval("!!vert.merge auto false morph:false disco:false")
lx.eval("select.typeFrom " + selmode)

    

