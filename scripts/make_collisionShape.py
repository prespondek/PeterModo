# python
# Title: Make Collision Box
# Author: Peter Respondek

# Makes a box around your selection in many different ways.

import lx
import sys
import time
import os
import re
import math

import modomath
import modoutil

numbersp = re.compile(r"\d+")

modoversion = lx.eval("query platformservice appversion ?")
selType = "all"
primitive = "cube"
alignment = "aligned"
verbose = False
connected = False
parts = False
sides = 8
delete = False
collision = False
threshold = 10
reduction = 0
collide = False
axis = "Y"
reducep = re.compile(r"(?<=reduce:)\d+",re.IGNORECASE)

if lx.eval("query scriptsysservice userValue.isdefined ? pr_collisionSelType"):
    selType = lx.eval("user.value pr_collisionSelType ?")
if lx.eval("query scriptsysservice userValue.isdefined ? pr_collisionPrimitive"):
    primitive = lx.eval("user.value pr_collisionPrimitive ?")
if lx.eval("query scriptsysservice userValue.isdefined ? pr_collisionAxis"):
    axis = lx.eval("user.value pr_collisionAxis ?")
if lx.eval("query scriptsysservice userValue.isdefined ? pr_CollisionHull_parts"):
    parts = lx.eval("user.value pr_CollisionHull_parts ?")
if lx.eval("query scriptsysservice userValue.isdefined ? pr_collisionAlignment"):
    alignment = lx.eval("user.value pr_collisionAlignment ?")
if lx.eval("query scriptsysservice userValue.isdefined ? pr_CollisionHull_connected"):
    connected = lx.eval("user.value pr_CollisionHull_connected ?")
if lx.eval("query scriptsysservice userValue.isdefined ? pr_CollisionHull_parts"):
    parts = lx.eval("user.value pr_CollisionHull_parts ?")
if lx.eval("query scriptsysservice userValue.isdefined ? pr_CollisionHull_delete"):
    delete = lx.eval("user.value pr_CollisionHull_delete ?")
if lx.eval("query scriptsysservice userValue.isdefined ? pr_CollisionHull_reduce") and \
   lx.eval("query scriptsysservice userValue.isdefined ? pr_CollisionHull_reduce_val"):   
    if lx.eval("user.value pr_CollisionHull_reduce ?"):
        reduction = lx.eval("user.value pr_CollisionHull_reduce_val ?")
if lx.eval("query scriptsysservice userValue.isdefined ? pr_collisionSides"):
    sides = lx.eval("user.value pr_collisionSides ?")

args = lx.args()
for arg in args:
    if arg == "connected":
        connected = True
    if arg == "verbose":
        verbose = True
    if arg == "profile":
        profile = True
    if arg == "delete":
        delete = True
    if arg == "parts":
        parts = True

    if arg == "cube" or \
       arg == "cylinder" or \
       arg == "convex":
        primitive = arg

    if arg == "axial" or \
       arg == "aligned":
        alignment = arg

    if arg == "X" or \
       arg == "Y" or \
       arg == "Z":
        axis = arg

    if arg == "delete":
        delete = True

    if arg == "collision":
        collision = True

    if reducep.search(arg):
        reduction = int(reducep.search(arg).group())

timer = time.clock()
selmode = lx.eval("query layerservice selmode ?")
threshold = math.radians(threshold)
num_layers = lx.eval("query layerservice layer.N ? all")
vertex_offset = 1 #this is an offset used when making obj
normal_offset = 1
object_list = []
m = lx.Monitor()

filename = "temp"
layer_list = modoutil.getLayerNames()
lx.out(layer_list)
while filename in layer_list:
    filename = modoutil.idGenerator()

obj_file = open ((lx.eval("query platformservice path.path ? user") + "\\" + filename + ".obj"), 'w')

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
    error ("Bad selection mode", "Only works with vertex, edge or polygon selection mode")
    sys.exit("LXe_ABORT")

# make sure we have enough points to make a hull
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
            
elif parts and not connected:
    part_list = list(modoutil.getPartsFromPolys(poly_index_list) - set([None,"Default",""]))
    for part in part_list:
        object_list.append(modoutil.Mesh(polys=modoutil.getPartPolys(part)))

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
        
    material = "textures\common\collision"    
    if not collision:
            material = lx.eval("query layerservice poly.material ? " + str(obj.render_poly_indices[0]))    
    if alignment == "axial" or primitive == "convex":
        if primitive == "cube":
            obj.addCollisionPolys(modoutil.buildCube(obj.getBBox(),material))
        elif primitive == "cylinder":
            obj.addCollisionPolys(modoutil.buildCylinder(obj.getBBox(),material))
        else:
            hull_pos_list, hull_polygon_list = modomath.qhull3d(obj.render_vert_pos, 0.0000001)
            modoutil.writeOBJ (obj_file, hull_pos_list, hull_polygon_list, material, vertex_offset, normal_offset)
            vertex_offset = vertex_offset + len(hull_pos_list)
            normal_offset = normal_offset + len(hull_polygon_list)
        
    else:
        #sub_timer = time.clock()
        if obj.target_poly_indices:
            best_axis = modoutil.getBestAxis(obj.target_poly_indices,threshold)
        else:
            best_axis = modoutil.getBestAxis(obj.render_poly_indices,threshold)
        obj.setMatrix(best_axis)
        old_rot = obj.euler
        obj.eulerUnRotateTo((0,0,0))
        obj.euler = (0,0,0)
        if primitive == "cube":
            obj.addCollisionPolys(modoutil.buildCube(obj.getBBox(),material))
        elif primitive == "cylinder":
            obj.addCollisionPolys(modoutil.buildCylinder(obj.getBBox(),material))
        obj.eulerRotateTo(old_rot)

obj_file.close()
      
    
if primitive == "convex":

    if modoversion >= 700:
        lx.eval("!!loaderOptions.wf_OBJ false true")  
    lx.eval("!!scene.open \"" + obj_file.name + "\" import")
    lx.eval("select.itemHierarchy " + filename)
    lx.eval("select.drop polygon")
    lx.eval("select.all")
    lx.eval("cut")
    lx.eval("select.layer " + str(layer))
    lx.eval("select.all")
    lx.eval("paste")
    lx.eval("select.invert")
    collision_polys = set(lx.eval("query layerservice polys ? selected")) 
    for obj in object_list:
            lx.command("select.element", layer=layer, type="polygon", mode="set", index=collision_polys.pop())
            lx.eval("select.connect")
            connected_polys = set(lx.eval("query layerservice polys ? selected"))
            obj.collision_poly_indices = connected_polys
            collision_polys = collision_polys.difference(connected_polys)
            
    lx.eval("select.item " + filename)
    if lx.eval("query sceneservice item.numChildren ? " + filename) > 1:
        for item in lx.eval("query sceneservice item.children ? " + filename):
            lx.eval("select.item " + item)
            lx.eval("item.delete")
    else:
        lx.eval("select.item " + lx.eval("query sceneservice item.children ? " + filename))
        lx.eval("item.delete")
    lx.eval("select.item " + filename)
    lx.eval("item.delete")
    lx.eval("select.layer " + str(layer))

lx.eval("select.drop polygon")

if reduction:
    for obj in object_list[::-1]: # i have to do the reduce in reverse order because poly indices are reordered.
        lx.eval("select.drop polygon")
        obj.selectCollisionPolys()
        lx.eval("tool.set poly.reduct on")
        lx.eval("tool.setAttr poly.reduct number " + str(reduction))
        lx.eval("tool.doApply")

if delete:
    lx.eval("select.drop polygon")
    for obj in object_list:
        obj.selectRenderPolys()
    lx.eval("delete")
        
for obj in object_list:
    lx.eval("select.drop polygon")
    obj.selectCollisionPolys()
    
    
    
            
