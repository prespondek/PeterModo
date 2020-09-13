# python
# Title: Polygon Merge
# Author: Peter Respondek

# This script works like regular polygon merge but also removes those unwanted
# vertices along the edge. You can give it an angle threshold if you want it to be more agressive.

# 5/6 : Fixed selected poly append fail

from itertools import izip
import lx
import time
import math

def error(titleString, errorString):
    lx.eval("dialog.setup error")
    lx.eval("dialog.title \"%s\"" % titleString)
    lx.eval("dialog.msg \"%s\"" % errorString)
    lx.eval("dialog.open")

def vecNorm(vec):
    return vecDotProduct(vec, vec) ** 0.5
def vecScalarMul(vec,scalar):
    return tuple(x * scalar for x in vec)
def vecNormalized(vec):
    return vecScalarMul(vec, 1.0 / vecNorm(vec)) 
def vecDotProduct(vec1, vec2):
    return sum(x1 * x2 for x1, x2 in izip(vec1, vec2))
def vecSub(vec1, vec2):
    return tuple(x - y for x, y in izip(vec1, vec2))
def vecAngle(vec1, vec2, vec3, vec4):
    try:
        return math.acos(vecDotProduct(vecNormalized(vecSub(vec1,vec2)),vecNormalized(vecSub(vec3,vec4))))
    except:
        #sometimes DP math can fuck up and produce values greater than 1 which causes acos to take a shit.
        return math.acos(1)

threshold = 0.1
args = lx.args()

if len(args) != 0:
    for arg in args:    
        try:
            threshold = float(arg)
        except:
            error("Invalid Number","This script takes floating point numbers only")
            sys.exit("LXe_INVALIDARG")

layer = lx.eval("query layerservice layers ? main")

threshold = math.radians(threshold)
lx.out(threshold)
lx.eval("select.drop vertex")
lx.eval("select.typeFrom polygon")
lx.eval("!poly.merge")
lx.eval("select.typeFrom polygon")
selected_polys = lx.eval("query layerservice polys ? selected")
if type(selected_polys) is str:
    selected_polys = tuple([selected_polys])
lx.out(selected_polys)
verts = []
for poly in selected_polys:
    lx.out(poly)
    poly_verts = (lx.eval("query layerservice poly.vertList ? " + str(poly)))
    for poly_vert in poly_verts:
        vert_list = lx.eval("query layerservice vert.vertList ? " + str(poly_vert))
        # lx.out(vert_list)
        if len(vert_list) <= 2:
            vert0_pos = lx.eval("query layerservice vert.pos ? " + str(poly_vert))
            vert1_pos = lx.eval("query layerservice vert.pos ? " + str(vert_list[0]))
            vert2_pos = lx.eval("query layerservice vert.pos ? " + str(vert_list[1]))
            # lx.out(vecSub(vert0_pos, vert1_pos))
            # lx.out(vecSub(vert2_pos, vert0_pos))
            # lx.out(vecAngle(vert0_pos, vert1_pos, vert2_pos, vert0_pos))
            if vecAngle(vert0_pos, vert1_pos, vert2_pos, vert0_pos) < threshold:
                verts.append(poly_vert)
if verts:
    lx.eval("select.drop vertex")
    for vert in verts:
        lx.command("select.element", layer=str(layer), type="vertex", mode="add", index=vert)
    lx.eval("vert.remove")

            
    
