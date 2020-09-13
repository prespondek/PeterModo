# python
# Title: T-Junction Fixer
# Author: Peter Respondek

# This script gets all the open edges in the selection and compares their distance to all the open vertices.
# If the distance is within the specified threshold the vertice will be welded onto that edge.
# Does various other checks to make sure bad things don't happen

# v1.1: added a bounding box check which makes this script about 3x faster
# v1.2: I load the scene into a grid like spactial data structure to reduce the
#       amount of vertex tests. Can speed up large scenes 10x.

from itertools import izip, imap
import lx
import time
import math
import re
import random
import string
import operator

SECTORS = 128

###############
# FUNCTIONS

def idGenerator(size=6, chars=string.ascii_letters + string.digits):
    return string.join(random.sample(chars,size),"")

def getBoundingBox(veclist, margin=0): 
    if not veclist: 
        return (0,0,0), (0,0,0) 

    dim = len(veclist[0]) 
    return ( tuple((min(vec[i] for vec in veclist)-margin for i in xrange(dim))), \
             tuple((max(vec[i] for vec in veclist)+margin for i in xrange(dim)))) 

def getBoxMagnitude (vec1, vec2):
    return (abs(vec1[0]) + abs(vec2[0]), abs(vec1[1]) + abs(vec2[1]), abs(vec1[2]) + abs(vec2[2]))
    
def divide (num1, num2):
    try:
        return num1 / num2
    except ZeroDivisionError:
        return 0
    
def error(titleString, errorString):
    lx.eval("dialog.setup error")
    lx.eval("dialog.title \"%s\"" % titleString)
    lx.eval("dialog.msg \"%s\"" % errorString)
    lx.eval("dialog.open")

def getCenterPoint(veclist):
    if not veclist: 
        return (0,0,0), 0 
    vecmin, vecmax = getBoundingBox(veclist) 
    return tuple((minco + maxco) * 0.5 for minco, maxco in izip(vecmin, vecmax))

def vecDistance(vec1, vec2):
    return vecNorm(vecSub(vec1, vec2))

def vecSub(vec1, vec2):
    return tuple(x - y for x, y in izip(vec1, vec2))

def vecAdd(vec1, vec2):
    return tuple(x + y for x, y in izip(vec1, vec2)) 

def vecNorm(vec):
    return vecDotProduct(vec, vec) ** 0.5

def vecNormalized(vec):
    return vecScalarMul(vec, divide(1.0, vecNorm(vec))) 

def vecScalarMul(vec,scalar):
    return tuple(x * scalar for x in vec)

def vecDotProduct(vec1, vec2):
    return sum(x1 * x2 for x1, x2 in izip(vec1, vec2))

def vecDistanceAxis(axis, vec):
    return vecNorm(vecNormal(axis[0], axis[1], vec)) / vecDistance(*axis)

def vecNormal(vec1, vec2, vec3):
    return vecCrossProduct(vecSub(vec2, vec1), vecSub(vec3, vec1))

def vecCrossProduct(vec1, vec2):
    return (vec1[1] * vec2[2] - vec1[2] * vec2[1],
            vec1[2] * vec2[0] - vec1[0] * vec2[2],
            vec1[0] * vec2[1] - vec1[1] * vec2[0])

def vecDistanceTriangle(triangle, vert):
    normal = vecNormal(*triangle)
    return vecDotProduct(normal, vecSub(vert, triangle[0])) \
           / vecNorm(normal)

# returns the angle between two lines in radians
def vecAngle(vec1, vec2, vec3, vec4):
    return math.acos(vecDotProduct(vecNormalized(vecSub(vec1,vec2)),vecNormalized(vecSub(vec3,vec4))))

def lineSamples(vec1, vec2, amount):
    pointList = []
    vec3 = getCenterPoint((vec1,vec2))
    if amount > 2:
        pointList.extend(lineSamples (vec1, vec3, amount * 0.5))
        pointList.append(vec3)
        pointList.extend(lineSamples (vec3, vec2, amount * 0.5))
    elif amount == 2:
        pointList = [vec3]
    else:
        pointList = []
    return (pointList)

def monstep (steps):
    try:
        m.step(steps)
    except:
        sys.exit("LXe_ABORT")
    

################
# GLOBALS

numbersp = re.compile(r"(\d+),(\d+)")
counter = 0
sector_space = [[[[] for x in range(SECTORS)] for y in range(SECTORS)] for z in range(SECTORS)]
total_time = time.clock()
layer = lx.eval("query layerservice layers ? main")
layer_bounds = lx.eval("query layerservice layer.bounds ? " + str(layer))
layer_bounds = (layer_bounds[0:3]),(layer_bounds[3:6])
sector_range = tuple(x/SECTORS for x in getBoxMagnitude(layer_bounds[0],layer_bounds[1]))
selmode = lx.eval("query layerservice selmode ?")

###############
# ARGUMENTS

args = lx.args()

threshold = 0

if len(args) == 0:
    try:
        lx.eval("user.defNew name:threshold type:float life:momentary")
        lx.eval("user.def threshold username {Distance Threshold}")
        lx.eval("user.value threshold")
    except:
        sys.exit("LXe_ABORT")

    threshold = lx.eval("user.value threshold ?")
    
else:
    for arg in args:    
        try:
            threshold = float(arg)
        except:
            error("Invalid Number","This script takes floating point numbers only")
            sys.exit("LXe_INVALIDARG")

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

###############
# SETUP

timer = time.clock()
selection_set = idGenerator()
num_sets = lx.eval("query layerservice polset.N ?")
if num_sets:
    set_names = []
    for x in range(num_sets):
        set_names.append(lx.eval("query layerservice polset.name ? " + str(x)))
    lx.out(str(set(set_names)) + str(set([selection_set])))
    while (set.intersection(set(set_names),set(selection_set))):
        selection_set = idGenerator()
lx.eval("select.editset " + selection_set + " add")
lx.eval("!!vert.merge fixed dist:" + str(threshold) + " disco:false")
lx.eval("select.useSet " + selection_set + " select")
selected_polys = lx.eval("query layerservice polys ? selected")
lx.eval("hide.unsel")
lx.eval("select.drop edge")
lx.eval("select.edge add poly equal 1")
open_edges = set(lx.eval("query layerservice edges ? selected")) 
lx.eval("select.drop edge")
lx.out(time.clock() - timer)
for edge in open_edges:
    x, y = edge[1:-1].split(',')
    lx.eval("select.element " + str(layer) + " edge add " + x + " " + y)
lx.eval("select.convert vertex")
open_vertices = lx.eval("query layerservice verts ? selected")
lx.out(time.clock() - timer)
for vertex in open_vertices:
    vert_pos = lx.eval("query layerservice vert.pos ? " + str(vertex))
    vert_range = tuple(int(math.ceil(x/y)-1) for x,y in izip(vecSub(layer_bounds[1],vert_pos), sector_range))
    sector_space[vert_range[0]][vert_range[1]][vert_range[2]].append(vertex)
m = lx.Monitor(len(open_edges))
lx.out(time.clock() - timer)

#################
# MAIN LOOP

for edge in open_edges:
    monstep(1)
    old_verts = []
    edge_sectors = []
    sector_vertices = []
    edge_vertices = lx.eval("query layerservice edge.vertList ? " + str(edge))
    vec1, vec2 = (lx.eval("query layerservice vert.pos ? " + str(edge_vertex)) for edge_vertex in edge_vertices)
    edge_bounds = getBoundingBox((vec1,vec2),threshold)
    sample_points = [vec1] + lineSamples (vec1, vec2, SECTORS) + [vec2]
    for point in sample_points:
        edge_sectors.append(tuple(int(math.ceil(x/y)-1) for x,y in izip(vecSub(layer_bounds[1],point), sector_range)))
    edge_sectors = set(edge_sectors)
    for sectors in edge_sectors:
        sector_vertices.extend(sector_space[sectors[0]][sectors[1]][sectors[2]])
    for vertex in sector_vertices:
        vec3 = lx.eval("query layerservice vert.pos ? " + str(vertex))

        #Check the vertex against the bounds of the edge
        if (vec3 != vec1 and vec3 != vec2) and \
           (vec3[0] > edge_bounds[0][0] and vec3[0] < edge_bounds[1][0]) and \
           (vec3[1] > edge_bounds[0][1] and vec3[1] < edge_bounds[1][1]) and \
           (vec3[2] > edge_bounds[0][2] and vec3[2] < edge_bounds[1][2]):
            vert_polys = set(lx.evalN("query layerservice vert.polyList ? " + str(vertex)))
            if not vert_polys:
                vert_polys = set([lx.eval1("query layerservice vert.polyList ? " + str(vertex))])
            edge_polys = set(lx.evalN("query layerservice edge.polyList ? " + str(edge)))
            if not edge_polys:
                edge_polys = set([lx.eval1("query layerservice edge.polyList ? " + str(edge))])
            
            if not edge_polys.intersection(vert_polys):         
                timer2 = time.clock()
                distance = vecDistanceAxis((vec1,vec2),vec3)
                try:
                    angle1 = vecAngle(vec1,vec2,vec1,vec3)
                except:
                    angle1 = 0
                try:
                    angle2 = vecAngle(vec2,vec1,vec2,vec3)
                except:
                    angle2 = 0
                if (distance <= threshold) and (math.degrees(angle1) < 90) and (math.degrees(angle2) < 90):
                    counter = counter + 1
                    hypotenuse1 = vecDistance(vec3,vec1)
                    hypotenuse2 = vecDistance(vec3,vec2)
                    length1 = math.cos(angle1) * hypotenuse1
                    length2 = math.cos(angle2) * hypotenuse2
                    percentage = length1  / (length1+length2)
                    if not old_verts:
                        lx.eval("tool.set edge.knife on")
                        lx.eval("tool.reset")
                        lx.eval("tool.attr edge.knife split false")
                    lx.eval("tool.attr edge.knife count " + str(len(old_verts) + 1))
                    lx.eval("tool.attr edge.knife vert0 " + str(layer - 1) + "," + str(edge_vertices[0]))
                    lx.eval("tool.attr edge.knife vert1 " + str(layer - 1) + "," + str(edge_vertices[1]))
                    lx.eval("tool.attr edge.knife pos " + str(percentage))
                    old_verts.append(vertex)

    if old_verts: 
        lx.eval("tool.doApply")
        lx.eval("tool.set edge.knife off")
        for x in range(len(old_verts)):
            new_vert_pos = lx.eval("query layerservice vert.pos ? " + str(lx.eval("query layerservice vert.n ? all") - (x+1)))
            lx.eval("vert.move vertIndex:" + str(old_verts[len(old_verts)-(x+1)]) + " posX:" + str(new_vert_pos[0]) + " posY:" + str(new_vert_pos[1]) + " posZ:" + str(new_vert_pos[2]))

lx.eval("select.typeFrom polygon")
lx.eval("select.useSet " + selection_set + " select")
lx.eval("!!vert.merge auto disco:false")
total_time = time.clock() - total_time
lx.eval("select.drop vertex")
lx.eval("select.drop edge")
lx.eval("select.drop polygon")
lx.eval("select.deleteSet " + selection_set + " select")
lx.eval("dialog.setup info")
lx.eval("dialog.title \"Operation Successful\"")
lx.eval("dialog.msg \"" + str(counter) + " T-Junctions fixed\nTotal time: " + str(total_time) + "\"")
lx.eval("dialog.open")
sys.exit("LXe_OK")
            
        
        





