# python
# Author: Peter Respondek and PFFI
# 
# This script copies the selected geometry to a new child layer. 
# Using the "collapse" arg will copy the current layer back into the parent
# layer if one exists. The "collapeAll" will copy all nested layers back to the
# root
#
# Both the default behavior and the "collapse" command and meant as a
# replacement for Hide and Unhide modo commands. In big scenes hiding geometry
# does jack for the performance so wrote this to quickly make new work layers. 


import lx
import re


def error(titleString, errorString):
    lx.eval("dialog.setup error")
    lx.eval("dialog.title \"%s\"" % titleString)
    lx.eval("dialog.msg \"%s\"" % errorString)
    lx.eval("dialog.open")


hide = False
collapse = False
collapseAll = False

args = lx.args()
for arg in args:
    if arg == "collapse":
        collapse = True
    if arg == "collapseAll":
        collapseAll = True
    if arg == "hide":
        hide = True
   
fg = lx.eval("query layerservice layers ? fg")
layer_name = lx.eval("query layerservice layer.name ? fg")
layer_id = lx.eval("query layerservice layer.id ? fg")

if collapse:
    parent_layer = lx.eval("query layerservice layer.parent ? fg")
    lx.out(parent_layer)
    if parent_layer == -1:
        sys.exit("LXe_ABORT")
    lx.eval("select.all")
    lx.eval("cut")
    lx.out (parent_layer)
    lx.eval("select.layer number:" + str(parent_layer + 1) + " mode:set")
    parent_id = lx.eval("query layerservice layer.id ? fg")
    lx.eval("paste")
    lx.eval("select.subItem item:" + layer_id + " mode:set mask:mesh")
    lx.eval("item.delete")
    lx.eval("select.subItem item:" + parent_id + " mode:set mask:mesh")
    sys.exit("LXe_SUCCESS")
        
if lx.eval("select.typeFrom {vertex;edge;polygon;item} ?"):
    lx.eval("select.drop polygon")
    selected_verts = lx.eval("query layerservice verts ? selected")
    polys = set()
    for vert in selected_verts:
        lx.out(str(vert))
        polys = polys | set(lx.eval("query layerservice vert.polyList ? " + str(vert)))
    lx.out(str(polys))
    for poly in polys:
        lx.eval("select.element layer:" + str(fg) + " type:polygon mode:add index:" + str(poly))
        
elif lx.eval("select.typeFrom {edge;polygon;item;vertex} ?"):
    lx.eval("select.drop polygon")
    selected_edges = lx.eval("query layerservice edges ? selected")
    polys = set()
    for edge in selected_edges:
        polys = polys | set(lx.eval("query layerservice edge.polyList ? " + str(edge)))
    for poly in polys:
        lx.eval("select.element layer:" + str(fg) + " type:polygon mode:add index:" + str(poly))

elif lx.eval("select.typeFrom {polygon;item;vertex;edge} ?"):
    pass

else:
    lx.out("No vertices, edges or polygons selected")
    sys.exit("LXe_NOTFOUND")

lx.eval("cut")
lx.eval("item.create type:mesh name:" + layer_name)
new_layer_index = lx.eval("query layerservice layer.index ? fg")
new_layer_id = lx.eval("query layerservice layer.id ? " + str(new_layer_index))
lx.out(new_layer_index)
lx.eval("item.parent " + new_layer_id + " " + layer_id + " inPlace:1")
lx.eval("paste")
lx.eval("select.all")

if hide:
    lx.eval("layer.setVisibility " + layer_id + " 0")

