# python

import lx
import re
import sys
import modomath

numbersp = re.compile(r"\d+")
polyselectp = re.compile(r"(?<=polyselect:)\d+",re.IGNORECASE)
polyselect = 0
fg = lx.eval("query layerservice layers ? main")

undotest = False
intersecttest = False
uvspeedtest = False

args = lx.args()
for arg in args:
    if arg == "uvspeedtest":
        uvspeedtest = True
    if arg == "undotest":
        undotest = True
    if arg == "intersecttest":
        intersecttest = True
    if polyselectp.search(arg):
        polyselect = int(polyselectp.search(arg).group())
    

if polyselect:
    lx.command("select.element", layer=fg, type="polygon", mode="set", index=polyselect)
    
if undotest:
    lx.out("Hello")
    lx.eval("select.drop polygon")
    lx.eval("select.all")
    lx.eval("poly.triple")
    lx.eval("app.undo")
    lx.out("Goodbye")
    sys.exit("LXe_SUCCESS")

if intersecttest:
    lx.eval("select.drop polygon")
    lx.eval("select.all")
    lx.eval("poly.triple")
    poly_index_list = lx.eval("query layerservice polys ? selected")
    tri_normals = []
    tris = []
    for poly in poly_index_list:
        tri_normals.append(lx.eval("query layerservice poly.normal ? " + str(poly)))
        poly_verts_pos = []
        for vert in lx.eval("query layerservice poly.vertList ? " + str(poly)):
            poly_verts_pos.append(lx.eval("query layerservice vert.pos ? " + str(vert)))
        tris.append(poly_verts_pos)
    ray = (0,-1,0)
    pos = (0,0,0)
    indicies, intersections = modomath.rayTriIntersection(ray, pos, tris, tri_normals)
    lx.out(ray, pos, tris, tri_normals)
    lx.out(indicies,   intersections)
    for intersection in intersections:
        lx.eval("tool.set prim.makeVertex on 0")
        lx.eval("tool.setAttr prim.makeVertex cenX " + str(intersection[0]))
        lx.eval("tool.setAttr prim.makeVertex cenY " + str(intersection[1]))
        lx.eval("tool.setAttr prim.makeVertex cenZ " + str(intersection[2]))
        lx.eval("tool.doApply")
        lx.eval("tool.set prim.makeVertex off")

if uvspeedtest:
    my_vmap = None
    vmaps = lx.eval("query layerservice vmaps ? texture")
    for vmap in lx.eval("query layerservice vmaps ? texture"):
        if lx.eval("query layerservice vmap.selected ? " + str(vmap)):
            my_vmap = vmap
            break
    poly_index_list = lx.eval("query layerservice polys ? selected")
    for poly in poly_index_list:
        poly_uvs = lx.eval("query layerservice poly.vmapValue ? " + str(poly))
        lx.out(poly_uvs)
    
