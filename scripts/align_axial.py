#python

import lx
import sys
import modomath
import math
import modoutil

def getNeighbourPolygons (poly_list):
    neighbour_polys_set = set()
    for poly in poly_list:
        for polyset in [lx.eval("query layerservice vert.polyList ? " + str (x)) \
                        for x in lx.eval("query layerservice poly.vertList ? " + str(poly))]:
            neighbour_polys_set = neighbour_polys_set.union(polyset)
    return neighbour_polys_set.difference(poly_list)

fg = lx.eval("query layerservice layers ? main")
selmode = lx.eval("query layerservice selmode ?")

args = lx.args()

threshold = 5

"""if len(args) == 0:
    lx.eval("user.defNew name:threshold life:momentary")
    lx.eval("user.def threshold username {Angle Threshold}")
    lx.eval("user.def threshold type float")
    lx.eval("user.value threshold")
    threshold = lx.eval("user.value threshold ?")"""

if selmode == "polygon":
    selected_polys_set = set([int(x) for x in lx.eval("query layerservice polys ? selected")])
    lx.out(selected_polys_set)
    planar_poly_list = []
    while (selected_polys_set):
        axis = None
        poly = selected_polys_set.pop()
        planar = True
        poly_normal = lx.eval("query layerservice poly.normal ? " + str(poly))
        axis_deg = [math.degrees(math.acos(modomath.vecDotProduct(x, tuple(abs(x) for x in poly_normal)))) for x in ((1,0,0),(0,1,0),(0,0,1))]
        if axis_deg[0] < threshold:
            axis = "X"
        if axis_deg[1] < threshold:
            axis = "Y"
        if axis_deg[2] < threshold:
            axis = "Z"
        if axis == None:
            continue
        lx.out(axis)
        planar_set = set([poly])
        not_planar_set = set()
        neighbour_polys_set = set(getNeighbourPolygons([poly]))
        while (planar):
            neighbour_polys_set = neighbour_polys_set.difference(planar_set)
            neighbour_polys_set = neighbour_polys_set.difference(not_planar_set) # get rid of the polygons we already know are non planar
            neighbour_polys = list(neighbour_polys_set)
            neighbour_normals = [lx.eval("query layerservice poly.normal ? " + str(x)) for x in neighbour_polys]
            planar_polys = []
            non_planar_polys = []
            for i in range(len(neighbour_normals)):
                angle_dif = 0
                if neighbour_normals[i] != poly_normal:
                    angle_dif = math.degrees(math.acos(modomath.vecDotProduct(neighbour_normals[i], poly_normal)))
                if angle_dif > threshold:
                    non_planar_polys.append(neighbour_polys[i])
                else:
                    planar_polys.append(neighbour_polys[i])
            if len(planar_polys) == 0:
                break
            planar_set = planar_set.union(planar_polys)
            not_planar_set = not_planar_set.union(non_planar_polys)
            neighbour_polys_set = getNeighbourPolygons(planar_polys)
        planar_poly_list.append(list(planar_set))
        selected_polys_set = selected_polys_set.difference(planar_set)

        
    
        
