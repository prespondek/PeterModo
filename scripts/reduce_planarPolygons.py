# python
# Title: Reduce Planar Polygons
# Author: Peter Respondek

# This script selects planar polygons within a given threshold
# and then merges them together. It's useful for creating simple collision
# models that do not need all the detail that artists cut into the model.

from itertools import izip
import lx
import time
import math
import re
import random
import string
import operator

numbersp = re.compile(r"\d+")

def idGenerator(size=6, chars=string.ascii_letters + string.digits):
    return string.join(random.sample(chars,size),"")

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
def vecAngle(vec1, vec2):
    try:
        return math.acos(vecDotProduct(vecNormalized(vec1),vecNormalized(vec2)))
    except:
        #sometimes DP math can fuck up and produce values greater than 1 which causes acos to take a shit.
        return math.acos(1)

args = lx.args()

threshold = 0

if len(args) == 0:
    try:
        lx.eval("user.defNew name:threshold type:float life:momentary")
        lx.eval("user.def threshold username {Angle Threshold}")
        lx.eval("user.value threshold")
        threshold = lx.eval("user.value threshold ?")
    except:
        sys.exit("LXe_ABORT")
    
else:
    for arg in args:    
        try:
            threshold = float(arg)
        except:
            error("Invalid Number","This script takes floating point numbers only")
            sys.exit("LXe_INVALIDARG")

counter = 0
total_time = time.clock()

layer = lx.eval("query layerservice layers ? main")
selmode = lx.eval("query layerservice selmode ?")
if selmode == 0:
    for vertex in lx.eval("query layerservice selection ? vert"):
        polys = lx.eval("query layerservice vert.polyList ? " + str(vertex))
        lx.eval("select.element " + str(layer) + " polygon add " + str(polys))
        
if selmode == 1:
    for edge in lx.eval("query layerservice selection ? edge"):
        polys = lx.eval("query layerservice edge.polyList ? " + str(edge))
        lx.eval("select.element " + str(layer) + " polygon add " + str(polys))
if selmode == 2:
    pass
if selmode == 3:
    pass


num_sets = lx.eval("query layerservice polset.N ?")
all_set_names = []
my_set_names = []
if num_sets:
    for x in range(num_sets):
        all_set_names.append(lx.eval("query layerservice polset.name ? " + str(x)))

planar_poly_set = []
planar_edge_set = []
selected_polys = lx.eval("query layerservice polys ? selected")
if selected_polys == None:
    lx.eval("select.all")
    selected_polys = lx.eval("query layerservice polys ? selected")
threshold = math.radians(threshold)
# lx.out (str(selected_polys))
# lx.out(layer)
m = lx.Monitor(len(selected_polys))

for poly in selected_polys:
    try:
        m.step(1)
    except:
        sys.exit("LXe_ABORT")
    poly_normal = lx.eval("query layerservice poly.normal ? " + str(poly))
    planar_poly_normal = 0
    if planar_poly_set:
        for x in range(len(planar_poly_set)):
            planar_poly_normal = lx.eval("query layerservice poly.normal ? " + str(planar_poly_set[x][0]))
            if vecAngle(poly_normal,planar_poly_normal) < threshold:
                # lx.out(str(poly) + " " + str(poly_normal))
                # lx.out(str(planar_poly_set[x][0]) + " " + str(planar_poly_normal))
                planar_poly_set[x].append(poly)
                break
            planar_poly_normal = 0
        if not planar_poly_normal:
            planar_poly_set.append([poly])           
    else:
        planar_poly_set.append([poly])
        
for planar_polys in planar_poly_set:
    lx.eval("select.drop polygon")
    for poly in planar_polys:
        lx.command("select.element", layer=str(layer), type="polygon", mode="add", index=poly)
    selection_set = idGenerator()
    while (set.intersection(set(all_set_names),set(selection_set))):
            selection_set = idGenerator()
    all_set_names.append(selection_set)
    my_set_names.append(selection_set)
    lx.eval("select.editset " + selection_set + " add")
# lx.out(my_set_names)

for selection_set in my_set_names:
    lx.eval("select.drop polygon")
    lx.eval("select.useSet " + selection_set + " select")
    lx.eval("!poly.merge")
    lx.eval("select.typeFrom polygon")
    selected_polys = lx.eval("query layerservice polys ? selected")
    # lx.out(selected_polys)
    verts = []
    for poly in selected_polys:
        # lx.out(poly)
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
                if vecAngle(vecSub(vert0_pos, vert1_pos),vecSub(vert2_pos, vert0_pos)) < threshold:
                    verts.append(poly_vert)
    if verts:
        lx.eval("select.drop vertex")
        for vert in verts:
            lx.command("select.element", layer=str(layer), type="vertex", mode="add", index=vert)
        lx.eval("vert.remove")
        
for selection_set in my_set_names:
    try:
        lx.eval("!!select.deleteSet " + selection_set)
    except:
        pass
            
        
        





