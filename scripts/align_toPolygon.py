# python
# Title: Make Collision Box
# Author: Peter Respondek

# Makes a box around your selection in many different ways.

import lx
import sys
import time
import os
import math

import modomath
import modoutil

selType = "all"
setpTarget = False
targetType = "world"
connected = False
threshold = 10
axis = "NegY"


if lx.eval("query scriptsysservice userValue.isdefined ? pr_collisionSelType"):
    selType = lx.eval("user.value pr_collisionSelType ?")
if lx.eval("query scriptsysservice userValue.isdefined ? pr_alignAxis"):
    axis = lx.eval("user.value pr_alignAxis ?")
if lx.eval("query scriptsysservice userValue.isdefined ? pr_CollisionHull_connected"):
    connected = lx.eval("user.value pr_CollisionHull_connected ?")
if lx.eval("query scriptsysservice userValue.isdefined ? pr_alignTargetType"):
    targetType = lx.eval("user.value pr_alignTargetType ?")


args = lx.args()
for arg in args:
    if arg == "connected":
        connected = True
    if arg == "delete":
        delete = True
    if arg == "NegX" or \
       arg == "NegY" or \
       arg == "NegZ" or \
       arg == "PosX" or \
       arg == "PosY" or \
       arg == "PosZ":
        axis = arg
    if arg == "setpTarget":
        setpTarget = True



compare_normal = (0,0,0)
if axis == "NegX":
    compare_normal = (-1,0,0)
elif axis == "NegY":
    compare_normal = (0,-1,0)
elif axis == "NegZ":
    compare_normal = (0,0,-1)
elif axis == "PosX":
    compare_normal = (1,0,0)
elif axis == "PosY":
    compare_normal = (0,1,0)
elif axis == "PosZ":
    compare_normal = (0,0,1)

lx.out(axis)
timer = time.clock()
selmode = lx.eval("query layerservice selmode ?")
threshold = math.radians(threshold)
num_layers = lx.eval("query layerservice layer.N ? all")
object_list = []
m = lx.Monitor()


layer_list = modoutil.getLayerNames()
lx.out(layer_list)

layer = lx.eval("query layerservice layers ? main")
            
vertex_index_list = set()
if selmode == "vertex":
    vertex_index_list = set(lx.eval("query layerservice verts ? selected"))
    lx.eval ("select.convert polygon") 
    poly_index_list = set(lx.eval("query layerservice polys ? selected"))
elif selmode == "edge":
    lx.eval ("select.convert vertex")        
    vertex_index_list = set(lx.eval("query layerservice verts ? selected"))
    lx.eval ("select.convert polygon") 
    poly_index_list = set(lx.eval("query layerservice polys ? selected"))
elif selmode == "polygon":
    poly_index_list = set(lx.eval("query layerservice polys ? selected"))
    lx.eval ("select.convert vertex")        
    vertex_index_list = set(lx.eval("query layerservice verts ? selected"))
else:
    modoutil.error ("Bad selection mode", "Only works with vertex, edge or polygon selection mode")
    sys.exit("LXe_ABORT")

if setpTarget:
    if poly_index_list:
        part_list = set()
        for part in lx.eval("query layerservice parts ? all"):
            part_list.add(lx.eval("query layerservice part.name ? " + str(part)))
        if "pr_target_part" in part_list:
            lx.eval("select.polygon set part face pr_target_part")
            lx.eval("poly.setPart Default")
        modoutil.selectPolygons(poly_index_list)
        lx.eval("poly.setPart pr_target_part")
        sys.exit("LXe_SUCCESS")
    else:
        modoutil.error("No Selection", "No polygons selected")
        sys.exit("LXe_ABORT")

if vertex_index_list == None:
    error("Convex Hull", "No geometry found.")
    
if connected:
    if selType == "polytarget":
        for connected_polys in modoutil.getConnectedPolyLists(poly_index_list):
            object_list.append(modoutil.Mesh(polys=connected_polys))
            object_list[len(object_list) - 1].target_poly_indices = list(poly_index_list.intersection(connected_polys))
    if selType == "all":
        for connected_polys in modoutil.getConnectedPolyLists(poly_index_list):
            object_list.append(modoutil.Mesh(polys=connected_polys))
else:
    if selType == "polytarget":
        connected_polys = modoutil.getConnectedPolys(poly_index_list)
        object_list.append (modoutil.Mesh(polys=connected_polys))
        target_polys = list(poly_index_list.intersection(connected_polys))
        object_list[0].target_poly_indices = target_polys
    else:        
        object_list.append (modoutil.Mesh(polys=poly_index_list))

m.init(len(object_list))

for obj in object_list:
    #timer = time.clock()
    try:
        m.step()
    except:
        sys.exit("LXe_ABORT")
        
    if obj.target_poly_indices:
        best_axis = modoutil.getBestAxis(obj.target_poly_indices,threshold)
    else:
        best_axis = modoutil.getBestAxis(obj.render_poly_indices,threshold)
    obj.setMatrix(best_axis)
    old_rot = obj.euler
    obj.eulerUnRotateTo((-0,-0,-0))
    obj.euler = (0,0,0)  
    obj.addCollisionPolys(modoutil.buildCube(obj.getBBox()))
    obj.eulerRotateTo(old_rot)
 

lx.eval("select.drop polygon")
if targetType == "world":
    for obj in object_list:
        obj.selectAllPolys()
    lx.eval("select.invert")
elif targetType == "polytarget":
    lx.eval("select.drop polygon")
    lx.eval("select.polygon add part face pr_target_part")
if not lx.eval("query layerservice polys ? selected"):
    modoutil.error("No Target Selection","There are no polygons in target selection")
modoutil.pasteAndSelect()    
lx.eval("poly.triple")
tri_normals = []
tris = []
world_poly_indicies = lx.eval("query layerservice polys ? selected")
for poly in world_poly_indicies:
    tri_normals.append(lx.eval("query layerservice poly.normal ? " + str(poly)))
    poly_verts_pos = []
    for vert in lx.eval("query layerservice poly.vertList ? " + str(poly)):
        poly_verts_pos.append(lx.eval("query layerservice vert.pos ? " + str(vert)))
    tris.append(poly_verts_pos)
lx.eval("delete")
for obj in object_list:
    lx.eval("select.drop polygon")
    collsion_index = obj.collision_poly_indices[0]
    best_normal = lx.eval("query layerservice poly.normal ? " + str(obj.collision_poly_indices[0]))
    best_dp = modomath.vecDotProduct(compare_normal,best_normal)
    for poly in obj.collision_poly_indices:
        normal = lx.eval("query layerservice poly.normal ? " + str(poly))
        dp = modomath.vecDotProduct(compare_normal,normal)
        if dp > best_dp:
            best_dp = dp
            collsion_index = poly
            best_normal = normal
    lx.command("select.element", layer=layer, type="polygon", mode="set", index=collsion_index)
    modoutil.pasteAndSelect()
    plane_verts = []
    for vert_index in lx.eval("query layerservice poly.vertList ? " + lx.eval("query layerservice polys ? selected")):
        plane_verts.append(lx.eval("query layerservice vert.pos ? " + str(vert_index)))
    lx.eval ("select.convert vertex")
    lx.eval ("!!vert.join true")
    pos_vert = lx.eval("query layerservice vert.N ? all") - 1
    pos = lx.eval("query layerservice vert.pos ? " + str(pos_vert))
    lx.command("select.element", layer=layer, type="vertex", mode="set", index=pos_vert)
    lx.eval("delete")
    indices, intersections = modomath.rayTriIntersection(compare_normal, pos, tris, tri_normals)
    if not indices:
        modoutil.error("No Geometry", "Did not collide against any geometry")
        sys.exit("LXe_ABORT")
    best_intersection = intersections[0]
    best_index = indices[0]
    shortest_distance = modomath.vecDotProduct(intersections[0], pos)
    for i in range(len(indices)):
        distance = modomath.vecDotProduct(intersections[i], pos)
        if distance > shortest_distance:
            shortest_distance = distance
            best_intersection = intersections[i]
            best_index = indices[i]

    target_normal = tri_normals[best_index]
    trans_vec = modomath.vecSub(best_intersection,pos)
    target2_normal = modomath.vecSub(modomath.linePlaneIntersection(compare_normal,plane_verts[0],target_normal,best_intersection,True,True),\
                                     modomath.linePlaneIntersection(compare_normal,plane_verts[1],target_normal,best_intersection,True,True))    
    target2_normal = modomath.vecNormalized(target2_normal)
    
    if axis == "PosX" or axis == "NegX":
        target_axis = modomath.orientMatrix((target_normal, target2_normal, modomath.vecCrossProduct(target_normal, target2_normal)),True,False,False)
    if axis == "PosY" or axis == "NegY":
        target_axis = modomath.orientMatrix((target2_normal, target_normal, modomath.vecCrossProduct(target_normal, target2_normal)),False,True,False)
    if axis == "PosZ" or axis == "NegZ":
        target_axis = modomath.orientMatrix((modomath.vecCrossProduct(target_normal, target2_normal), target2_normal, target_normal),False,False,True)
    modoutil.debugAxis(target_axis, best_intersection)
    modoutil.debugAxis(modomath.orientMatrix(obj.matrix), pos)
    obj.setMatrix(modomath.orientMatrix(obj.matrix))
    target_euler = modomath.matrixToEular(target_axis,True)
    obj.eulerRotateTo(target_euler, pos)
    modoutil.transformMove(trans_vec)
    lx.eval("select.drop polygon")
    obj.selectCollisionPolys()
    lx.eval("delete")
    
    

    
    
    
            
