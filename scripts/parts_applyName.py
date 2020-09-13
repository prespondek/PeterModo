# python
# Title: Apply Part Name
# Author: Peter Respondek

# Applys a new part name in any flavor you desire. Avoids name clashing.
# connected flag will do all connected polygons

import lx

connected = False

args = lx.args()
for arg in args:
    if arg == "connected":
        connected = True

fg = lx.eval("query layerservice layers ? fg")
lx.eval("unhide")
num_parts = lx.eval("query layerservice part.N ? all")
parts_list=set()

for i in range(num_parts):
    parts_list = parts_list.union([lx.eval("query layerservice part.name ? " + str(i))])
parts_list = parts_list - set([None,"Default",""])
if connected:
    lx.eval("select.drop polygon")
    lx.eval("select.all")
    for part in parts_list:
        lx.eval("select.polygon remove part face " + str(part))
    poly_index_list = set(lx.eval("query layerservice polys ? selected"))
    i = 1
    while poly_index_list:
        for poly in poly_index_list:
            lx.command("select.element", layer=fg, type="polygon", mode="set", index=poly)
            lx.eval("select.connect")
            poly_index_list = poly_index_list.difference(set(lx.eval("query layerservice polys ? selected")))
            lx.out(parts_list)
            while str(i) in parts_list:
                i += 1
            lx.eval("poly.setPart " + str(i))
            num_parts += 1
            parts_list = parts_list | set([str(i)])
            break
else:
    i = 1
    while str(i) in parts_list:
                i += 1
    lx.eval("poly.setPart " + str(i))


