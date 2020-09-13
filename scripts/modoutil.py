# This is a python conversion of seneca's "script_goodSubroutines" perl library, plus some of my own stuff

import lx
import modomath
import os
import string
import random
import re
import math

layer = lx.eval("query layerservice layers ? main")
numbersp = re.compile(r"\d+")

def queryUserValue(user_val):
    if lx.eval("query scriptsysservice userValue.isdefined ? " + str(user_val)):
        return lx.eval("user.value " + str(user_val) + " ?")
    else:
        return None

def getLayerNames():
    layer_list = []
    for i in range(1, lx.eval("query layerservice layer.N ? all") ):
        layer_list.append(lx.eval("query layerservice layer.name ? " + str(i)))
    return layer_list

def idGenerator(size=6, chars=string.ascii_letters + string.digits):
    return string.join(random.sample(chars,size),"")

def getUniqueSelSetName(polys):
    sel_sets = set()
    for poly in polys:
        sel_sets += set(lx.eval("query layerservice poly.selSets ? " + str(poly)))

    rand_id = idGenerator()
    while rand_id in sel_sets:
        rand_id = idGenerator()
    return rand_id

def modoUserDef(name_cmd,type_cmd,life_cmd,username_cmd,list_cmd,listnames_cmd,argtype_cmd,min_cmd,max_cmd,action_cmd,value_cmd):
    if lx.eval("query scriptsysservice userValue.isdefined ? " + name_cmd) == False:
        lx.out("Setting up " + name_cmd + "--------------------------")
        lx.out(name_cmd + " " + type_cmd + " " + life_cmd + " " + username_cmd + " " + list_cmd + " " + listnames_cmd + " " + \
               argtype_cmd + " " + min_cmd + " " + max_cmd + " " + action_cmd + " " + value_cmd)
        lx.out(name_cmd + " didn't exist yet so I'm creating it.")
        lx.eval("user.defNew name:" + name_cmd + " type:" + type_cmd + " life:" + life_cmd)
        if username_cmd:
            lx.out("running user value setup 3 \"" + username_cmd + "\"")
            lx.eval("user.def " + name_cmd + " username \"" + username_cmd + "\"")
        if list_cmd:
            lx.out("running user value setup 4")
            lx.eval("user.def " + name_cmd + " list " + list_cmd)	    
        if listnames_cmd:
            lx.out("running user value setup 5")
            lx.eval("user.def " + name_cmd + " listnames " + listnames_cmd)
        if argtype_cmd:
            lx.out("running user value setup 6")
            lx.eval("user.def " + name_cmd + " argtype " + argtype_cmd)		
        if min_cmd != "xxx":
            lx.out("running user value setup 7")
            lx.eval("user.def " + name_cmd + " min " + min_cmd)
        if max_cmd != "xxx":
            lx.out("running user value setup 8")
            lx.eval("user.def " + name_cmd + " max " + max_cmd)
        if action_cmd:
            lx.out("running user value setup 9")
            lx.eval("user.def " + name_cmd + " action " + action_cmd)
        if not value_cmd:
            lx.out("woah.  there's no value in the userVal sub!")
            lx.out("user.defDelete " + name_cmd)
            sys.exit("LXe_ABORT")
        lx.out("running user value setup 10")
        lx.eval("user.value "+ name_cmd + " " + value_cmd )
        
    else:
        #STRING-------------
        if type_cmd == "string":
                if lx.eval("user.value " + name_cmd + " ?") == None:
                        lx.out("user value " + name_cmd + " was a blank string")
                        lx.eval("user.value " + name_cmd + " " + value_cmd)
        #BOOLEAN------------
        elif type_cmd == "boolean":
            pass
        #LIST---------------
        elif username_cmd:
                if lx.eval("user.value " + name_cmd + " ?") == -1:
                    lx.out("user value " + name_cmd + " was a blank list")
                    lx.eval("user.value " + name_cmd + " " + value_cmd)

        #ALL OTHER TYPES----
        elif lx.eval("user.value " + name_cmd + " ?") == None:
            lx.out("user value " + name_cmd + " was a blank number")
            lx.eval("user.value " + name_cmd + " " + value_cmd)

def getBestAxis(poly_indices,threshold):
    planar_poly_set, planar_normals_set, planar_area_set = getPlanarPolys(poly_indices,threshold)
    a_axis = 0
    b_axis = 0
    c_axis = 0
    a_axis_index = 0
    b_axis_index = 0
    best_edge_index = []
    largest_area = 0
    for x in range(len(planar_area_set)):
        if planar_area_set[x] > largest_area:
            largest_area = planar_area_set[x]
            a_axis_index = x
    a_axis = planar_normals_set[a_axis_index]
    lx.eval("select.drop edge")
    lx.eval("select.drop polygon")
    for poly in planar_poly_set[a_axis_index]:
        lx.command("select.element", layer=layer, type="polygon", mode="add", index=poly)
    lx.eval("select.boundary")
    edges = lx.eval("query layerservice edges ? selected")
    max_distance = 0
    best_edge = ()
    for edge in edges:
        x, y = numbersp.findall(edge)
        x = lx.eval("query layerservice vert.pos ? " + x)
        y = lx.eval("query layerservice vert.pos ? " + y)
        distance = modomath.vecDistance(x, y)
        if distance > max_distance:
            max_distance = distance
            best_edge = [x, y]
            best_edge_index = edge
    b_axis = modomath.vecNormalized(modomath.vecSub(best_edge[0],best_edge[1]))
    c_axis = modomath.vecCrossProduct(a_axis,b_axis)
    return a_axis,b_axis,c_axis

def getLongestEdge(poly_indices):
    if type(poly_indices) != tuple:
        poly_indices = tuple(poly_indices)

    length = 0
    longest = (0,0)

    for poly in poly_indices:
        verts = lx.eval("query layerservice poly.vertList ? " + str(poly))
        for i,j in zip(range(len(verts))[0::1] + [len(verts)-1], range(len(verts))[1::1] + [0]):
            edge_length = lx.eval("query layerservice edge.length ? " + str(verts[i]) + "," + str(verts[j]))
            if edge_length > length:
                length = edge_length
                longest = (verts[i], verts[j])
    return longest

def getMostCumulativeEdge(poly_indices):
    if type(poly_indices) != tuple:
        poly_indices = tuple(poly_indices)

    length = 0
    longest = (0,0)

    for poly in poly_indices:
        verts = lx.eval("query layerservice poly.vertList ? " + str(poly))
        for i,j in zip(range(len(verts))[0::1] + [len(verts)-1], range(len(verts))[1::1] + [0]):
            edge_length = lx.eval("query layerservice edge.length ? " + str(verts[i]) + "," + str(verts[j]))
            if edge_length > length:
                length = edge_length
                longest = (verts[i], verts[j])
    return longest
    
def getPlanarPolys(poly_indices,threshold):
    poly_areas = []
    poly_normals = []
    for poly in poly_indices:
        poly_verts_pos = []
        poly_normal = lx.eval("query layerservice poly.normal ? " + str(poly))
        poly_normals.append(poly_normal)
        poly_verts = lx.eval("query layerservice poly.vertList ? " + str(poly))
        for vert in poly_verts:
            poly_verts_pos.append(lx.eval("query layerservice vert.pos ? " + str(vert)))
        try:
            poly_areas.append(modomath.area3D_Polygon(poly_verts_pos, poly_normal))
        except:
            lx.out("Bad polygon detected")
            lx.out("Polygon index: " + poly)
            poly_areas.append(0)
    planar_normals_set = [poly_normals[0]]
    planar_poly_set = [[poly_indices[0]]]
    planar_area_set = [poly_areas[0]]
    for x in (range(1,len(poly_indices))):
        new_poly = True
        for y in (range(len(planar_normals_set))):
            # lx.out(str(planar_normals_set[y]) + " " + str(poly_indices[x]) + " " + str(math.degrees(vecAngle(poly_normals[x],planar_normals_set[y]))))
            if modomath.vecAngle(poly_normals[x],planar_normals_set[y]) < threshold:
                planar_poly_set[y].append(poly_indices[x])
                planar_area_set[y] = planar_area_set[y] + poly_areas[x]
                new_poly = False
                break
        if new_poly:
            planar_poly_set.append   ([poly_indices[x]])
            planar_normals_set.append(poly_normals[x])
            planar_area_set.append   (poly_areas[x])     
    return planar_poly_set, planar_normals_set, planar_area_set

def getConnectedPolyLists(polygon_index_list):
    connected_poly_list = []
    while polygon_index_list:
        for source_polygon in polygon_index_list:
            lx.eval("select.drop polygon")
            lx.command("select.element", layer=layer, type="polygon", mode="set", index=source_polygon)
            lx.eval("select.connect")
            connected_polys = set(lx.eval("query layerservice polys ? selected"))
            connected_poly_list.append (list(polygon_index_list.intersection(connected_polys)))
            polygon_index_list = polygon_index_list.difference(connected_polys)
            break
    return list(connected_poly_list)

def getConnectedPolys(polygon_index_list):
    connected_poly_list = []
    lx.eval("select.drop polygon")
    for source_polygon in polygon_index_list:
        lx.command("select.element", layer=layer, type="polygon", mode="set", index=source_polygon)
    lx.eval("select.connect")
    return lx.eval("query layerservice polys ? selected")

def getPartPolys(part):
    lx.eval("select.drop polygon")
    lx.eval("select.polygon add part face " + str(part))
    return lx.eval("query layerservice polys ? selected")

def getVertsFromPolys(polygon_index_list):
    vertex_list = set()
    for source_polygon in polygon_index_list:
        poly_verts = lx.eval("query layerservice poly.vertList ? " + str(source_polygon))
        vertex_list = vertex_list.union(poly_verts)
    return list(vertex_list)
        
def getPolysFromVerts(vertex_index_list):
    polygon_list = set()
    for source_vertex in vertex_index_listt:
        vert_polys = lx.eval("query layerservice vert.polyList ? " + str(source_vertex))
        polygon_list = polygon_list.union(vert_polys)
    return list(polygon_list)

def getPartsFromPolys(polygon_index_list):
    part_list = set()
    for source_polygon in polygon_index_list:
        part_list = part_list.union(lx.eval("query layerservice poly.part ? " + str(source_polygon)))
    return part_list

def peeler(edge_list):
    mainlayer = lx.eval("query layerservice layers ? main")
    for edges in edge_list:
        polys = lx.evalN("query layerservice edge.polyList ? " + str(edges[0][0]) + "," + str(edges[0][1]))
        lx.eval("select.type polygon")
        lx.eval("select.element " + str(mainlayer) + " polygon set " + str(polys[0]))
        lx.eval("select.connect")
        lx.eval("uv.delete")
        lx.eval("select.drop edge")
    for edge in edges:
        lx.eval("select.element " + str(mainlayer) + " edge add " + str(edge[0]) + " " + str(edge[1]))
    lx.eval("tool.set uv.peeler on")
    lx.eval("tool.reset")
    lx.eval("tool.doApply")
    lx.eval("tool.set uv.peeler off")

def getBoundarySideFromPolys(polygon_index_set):
    mainlayer = lx.eval("query layerservice layers ? main")
    edge_list = []

    while polygon_index_set:
        lx.eval("!!select.drop polygon")
        lx.eval("!!select.element " + str(mainlayer) + " polygon set " + str(polygon_index_set.pop()))
        lx.eval("!!select.connect")
        current_polys = lx.eval("query layerservice polys ? selected")
        lx.eval("!!select.drop edge")
        lx.eval("!!select.type polygon")
        lx.eval("!!select.boundary")
        boundary_edges = set(eval(x) for x in lx.eval("query layerservice edges ? selected"))
        
        loop_edges = []
        while boundary_edges:
            boundary_edge = boundary_edges.pop()
            lx.eval("select.element " + str(mainlayer) + " edge set " + str(boundary_edge[0]) + " " + str(boundary_edge[1]))
            lx.eval("select.loop")
            loop_edges.append([eval(x) for x in lx.eval("query layerservice edges ? selected")])
            boundary_edges -= set(loop_edges[len(loop_edges) - 1])
            
        lx.out(len(loop_edges))
        lx.out(loop_edges)
        if len(loop_edges) > 2:
            error ("Bad Selection", "Polygon selection has holes")
            sys.exit( "LXe_FAILED:Script failed" )
        if len(loop_edges) == 2:
            error ("Bad Selection", "You selection is a polygon loop")
            sys.exit( "LXe_FAILED:Script failed" )
            
        edge_verts = set()
        for poly in current_polys:
            edge_verts = edge_verts.symmetric_difference(set(lx.eval("query layerservice poly.vertList ? " + str(poly))))
        if len(edge_verts) != 4:
            error ("Bad Selection", "Selection contains broken polygons loops or has polygons with more or less than four vertices. Quads only")
            sys.exit( "LXe_FAILED:Script failed" )

        edge_vert = edge_verts.pop()
        shortest_edge_vert = 0
        steps = 0
        lx.eval("select.type vertex")
        while edge_verts:
            lx.eval("select.element " + str(mainlayer) + " vert set " + str(edge_vert))
            test_vert = edge_verts.pop()
            lx.eval("select.element " + str(mainlayer) + " vert add " + str(test_vert))
            lx.eval("select.between")
            current_steps = lx.eval("query layerservice vert.N ? selected")
            if current_steps < steps or steps == 0:
                steps = current_steps
                shortest_edge_vert = test_vert

        lx.eval("select.element " + str(mainlayer) + " vert set " + str(edge_vert))
        lx.eval("select.element " + str(mainlayer) + " vert add " + str(shortest_edge_vert))
        lx.eval("select.between")
        lx.eval("select.convert edge")
        
        edge_list.append([eval(x) for x in lx.evalN("query layerservice edges ? selected")])
        
        polygon_index_set -= set(current_polys)

    lx.eval("!!select.drop edge")
    for edges in edge_list:
        for edge in edges: 
            lx.eval("select.element " + str(mainlayer) + " edge add " + str(edge[0]) + " " + str(edge[1]))
    return edge_list

def selectPolygons(poly_index_list, setp=True):
    if setp:
        lx.eval("select.drop polygon")
    if poly_index_list:
        for poly in poly_index_list:
                lx.command("select.element", layer=layer, type="polygon", mode="add", index=poly)
        return True
    else:
        return False

def writeOBJ (obj_file, hull_pos_list, hull_polygon_list, material, vertex_offset, normal_offset):
    #obj_file.seek(0, os.SEEK_END)
    obj_file.write ("o Mesh\n")
    for verts in hull_pos_list:
        obj_file.write ("v " + str(verts[0]) + " " + str(verts[1]) + " " + str(verts[2]) + "\n")
    for indices in hull_polygon_list:
        faceNormal = modomath.vecNormal(hull_pos_list[indices[0]],hull_pos_list[indices[1]],hull_pos_list[indices[2]])
        obj_file.write ("vn " + str(faceNormal[0]) + " " + str(faceNormal[1]) + " " + str(faceNormal[2]) + "\n")
    obj_file.write ("usemtl " + material + "\n")
    obj_file.write ("g " + material + "\n")
    for i, indices in enumerate(hull_polygon_list):
        obj_file.write ("f " + str(vertex_offset+indices[0]) + "//" + str(normal_offset+i) +
                        " " + str(vertex_offset+indices[1]) + "//" + str(normal_offset+i) +
                        " " + str(vertex_offset+indices[2]) + "//" + str(normal_offset+i) + "\n")
    obj_file.flush()
    os.fsync(obj_file.fileno())

def resetXfrm():
    lx.eval("tool.setAttr axis auto startX 0.0")
    lx.eval("tool.setAttr axis auto startY 0.0")
    lx.eval("tool.setAttr axis auto startZ 0.0")
    lx.eval("tool.setAttr axis auto endX 0.0")
    lx.eval("tool.setAttr axis auto endY 0.0")
    lx.eval("tool.setAttr axis auto endZ 0.0")
    lx.eval("tool.setAttr xfrm.transform TX 0.0")
    lx.eval("tool.setAttr xfrm.transform TY 0.0")
    lx.eval("tool.setAttr xfrm.transform TZ 0.0")
    lx.eval("tool.setAttr xfrm.transform RX 0.0")
    lx.eval("tool.setAttr xfrm.transform RY 0.0")
    lx.eval("tool.setAttr xfrm.transform RZ 0.0")
    lx.eval("tool.setAttr xfrm.transform U 0.0")
    lx.eval("tool.setAttr xfrm.transform V 0.0")

def pasteAndSelect():
    lx.eval("copy")
    lx.eval("select.all")
    lx.eval("paste")
    lx.eval("select.invert")

def rotateZ(angle,pos=None):
    lx.eval("tool.set TransformRotate on")
    if pos:
        lx.eval("tool.set actr.auto on")
        lx.eval("tool.setAttr center.auto cenX " + str(pos[0]))
        lx.eval("tool.setAttr center.auto cenY " + str(pos[1]))
        lx.eval("tool.setAttr center.auto cenZ " + str(pos[2]))
    lx.eval("tool.setAttr xfrm.transform RZ " + str(angle))
    lx.eval("tool.setAttr xfrm.transform RX 0.0")
    lx.eval("tool.setAttr xfrm.transform RY 0.0")
    lx.eval("tool.doApply")

def rotateY(angle,pos=None):
    lx.eval("tool.set TransformRotate on")
    if pos:
        lx.eval("tool.set actr.auto on")
        lx.eval("tool.setAttr center.auto cenX " + str(pos[0]))
        lx.eval("tool.setAttr center.auto cenY " + str(pos[1]))
        lx.eval("tool.setAttr center.auto cenZ " + str(pos[2]))
    lx.eval("tool.setAttr xfrm.transform RY " + str(angle))
    lx.eval("tool.setAttr xfrm.transform RX 0.0")
    lx.eval("tool.setAttr xfrm.transform RZ 0.0")
    lx.eval("tool.doApply")

def rotateX(angle,pos=None):
    lx.eval("tool.set TransformRotate on")
    if pos:
        lx.eval("tool.set actr.auto on")
        lx.eval("tool.setAttr center.auto cenX " + str(pos[0]))
        lx.eval("tool.setAttr center.auto cenY " + str(pos[1]))
        lx.eval("tool.setAttr center.auto cenZ " + str(pos[2]))
    lx.eval("tool.setAttr xfrm.transform RX " + str(angle))
    lx.eval("tool.setAttr xfrm.transform RY 0.0") 
    lx.eval("tool.setAttr xfrm.transform RZ 0.0")
    lx.eval("tool.doApply")

def transformMove(vec):
    lx.eval("tool.set TransformMove on")
    lx.eval("tool.setAttr xfrm.transform TX " + str(vec[0]))
    lx.eval("tool.setAttr xfrm.transform TY " + str(vec[1])) 
    lx.eval("tool.setAttr xfrm.transform TZ " + str(vec[2])) 
    lx.eval("tool.doApply")

def buildCube(bbox, material='textures/common/collision'):
    sizeX = (bbox[0][0] - bbox[1][0])
    sizeY = (bbox[0][1] - bbox[1][1])
    sizeZ = (bbox[0][2] - bbox[1][2])
    centerX = bbox[1][0] + (sizeX / 2)
    centerY = bbox[1][1] + (sizeY / 2)
    centerZ = bbox[1][2] + (sizeZ / 2)
         
    lx.eval("tool.set prim.cube on")
    lx.eval("tool.setAttr prim.cube cenX " + str(centerX))
    lx.eval("tool.setAttr prim.cube cenY " + str(centerY))
    lx.eval("tool.setAttr prim.cube cenZ " + str(centerZ))
    lx.eval("tool.setAttr prim.cube sizeX " + str(sizeX))
    lx.eval("tool.setAttr prim.cube sizeY " + str(sizeY))
    lx.eval("tool.setAttr prim.cube sizeZ " + str(sizeZ))
    lx.eval("tool.setAttr prim.cube segmentsX 1")
    lx.eval("tool.setAttr prim.cube segmentsY 1")
    lx.eval("tool.setAttr prim.cube segmentsZ 1")
    lx.eval("tool.setAttr prim.cube axis 0")
    lx.eval("tool.doApply")
    lx.eval("tool.set prim.cube off")
    lastpoly = lx.eval("query layerservice poly.index ? last")
    lx.eval("select.type polygon")
    lx.eval("select.element layer:" + str(layer) + " type:polygon mode:set index:" + lastpoly)
    lx.eval("select.connect")
    lx.eval("poly.setMaterial name:" + material) 
    return (lx.eval("query layerservice polys ? selected"))

def buildCylinder(bbox, material="textures\common\collision", sides=8, axis="X"):
    sizeX = (bbox[0][0] - bbox[1][0])
    sizeY = (bbox[0][1] - bbox[1][1])
    sizeZ = (bbox[0][2] - bbox[1][2])
    centerX = bbox[1][0] + (sizeX / 2)
    centerY = bbox[1][1] + (sizeY / 2)
    centerZ = bbox[1][2] + (sizeZ / 2)
    
    lx.eval("tool.set prim.cylinder on")
    lx.eval("tool.setAttr prim.cylinder cenX " + str(centerX))
    lx.eval("tool.setAttr prim.cylinder cenY " + str(centerY))
    lx.eval("tool.setAttr prim.cylinder cenZ " + str(centerZ))
    lx.eval("tool.setAttr prim.cylinder sizeX " + str(sizeX/2))
    lx.eval("tool.setAttr prim.cylinder sizeY " + str(sizeY/2))
    lx.eval("tool.setAttr prim.cylinder sizeZ " + str(sizeZ/2))
    lx.eval("tool.setAttr prim.cylinder sides " + str(sides))
    if axis == "X": lx.eval("tool.setAttr prim.cylinder axis 0")
    if axis == "Y": lx.eval("tool.setAttr prim.cylinder axis 1")
    if axis == "Z": lx.eval("tool.setAttr prim.cylinder axis 2")
    lx.eval("tool.doApply")
    lx.eval("tool.set prim.cylinder off")
    lastpoly = lx.eval("query layerservice poly.index ? last")
    lx.eval("select.drop polygon")
    lx.eval("select.element layer:" + str(layer) + " type:polygon mode:set index:" + lastpoly)
    lx.eval("select.connect")
    lx.eval("poly.setMaterial name:" + material) 
    return (lx.eval("query layerservice polys ? selected"))
    
def error(titleString, errorString):
    lx.eval("dialog.setup error")
    lx.eval("dialog.title \"%s\"" % titleString)
    lx.eval("dialog.msg \"%s\"" % errorString)
    lx.eval("dialog.open")

def makeVertex(vec):
    lx.eval("tool.set prim.makeVertex on 0")
    lx.eval("tool.setAttr prim.makeVertex cenX " + str(vec[0]))
    lx.eval("tool.setAttr prim.makeVertex cenY " + str(vec[1]))
    lx.eval("tool.setAttr prim.makeVertex cenZ " + str(vec[2]))
    lx.eval("tool.doApply")
    lx.eval("tool.set prim.makeVertex off 0")


# debug function to draw an axis
def debugAxis (matrix, pos=(0,0,0)):
    for i in range(len(matrix)):
        lx.eval("tool.set prim.tube on")
        lx.eval("tool.attr prim.tube sides 4")
        lx.eval("tool.attr prim.tube segments 1")
        lx.eval("tool.attr prim.tube radius 0.0188")
        lx.eval("tool.attr prim.tube caps false")
        lx.eval("tool.attr prim.tube mode add")
        lx.eval("tool.attr prim.tube number 1")
        lx.eval("tool.attr prim.tube ptX " + str(matrix[i][0] + pos[0]))
        lx.eval("tool.attr prim.tube ptY " + str(matrix[i][1] + pos[1]))
        lx.eval("tool.attr prim.tube ptZ " + str(matrix[i][2] + pos[2]))
        lx.eval("tool.attr prim.tube number 2")
        lx.eval("tool.attr prim.tube ptX " + str(pos[0]))
        lx.eval("tool.attr prim.tube ptY " + str(pos[1]))
        lx.eval("tool.attr prim.tube ptZ " + str(pos[2]))
        lx.eval("tool.doapply")
        lx.eval("select.drop polygon")
        poly_count = lx.eval("query layerservice poly.N ? all")
        for poly in range(poly_count - 4, poly_count):
            lx.command("select.element", layer=layer, type="polygon", mode="add", index=poly)
        if i == 0:
            lx.eval("poly.setMaterial x {1.0 0.0 0.0} 0.8 0.2 true false")
        elif i == 1:
            lx.eval("poly.setMaterial y {0.0 1.0 0.0} 0.8 0.2 true false")
        else:
            lx.eval("poly.setMaterial z {0.0 0.0 1.0} 0.8 0.2 true false")
    lx.eval("select.drop polygon")

class Mesh:
    render_vert_indices = []
    render_vert_pos = []
    render_poly_indices = []
    target_poly_indices = []
    collision_poly_indices = []
    pivot = (0,0,0)
    euler = (0,0,0)
    matrix = [[1,0,0], \
              [0,1,0], \
              [0,0,1]]

    # Constructor
    def __init__(self, verts=None, polys=None):
        lx.out(verts)
        lx.out(polys)
        if not verts and polys:
            verts = getVertsFromPolys(polys)
        if not polys and verts:
            polys = getPolysFromVerts(verts)
            
        self.render_vert_indices = list(verts)
        self.render_poly_indices = list(polys)
        
        self.updateVecPos()

    def updateVecPos(self):
        if not self.render_vert_indices:
            return
        self.render_vert_pos = []
        x_avg = y_avg = z_avg = 0
        for vert in self.render_vert_indices:
            vert_pos = lx.eval("query layerservice vert.pos ? " + str(vert))
            x_avg = x_avg + vert_pos[0]
            y_avg = y_avg + vert_pos[1]
            z_avg = z_avg + vert_pos[2]
            self.render_vert_pos.append(vert_pos)
        try:
            self.pivot = x_avg / len(self.render_vert_indices), y_avg / len(self.render_vert_indices), z_avg / len(self.render_vert_indices)
        except:
            lx.out(str(self.render_vert_indices) + " " + str(x_avg) + " " + str(y_avg) + " " + str(z_avg))
        
    def addRenderPolys (self, polys):
        self.render_poly_indices.extend(polys)

    def addCollisionPolys (self, polys):
        self.collision_poly_indices.extend(polys)
        
    def setMatrix (self, matrix):
        self.matrix = matrix
        self.euler = modomath.matrixToEular(matrix)
        self.euler = math.degrees(self.euler[0]),math.degrees(self.euler[1]),math.degrees(self.euler[2])
        
    def selectRenderPolys(self):
        for poly in self.render_poly_indices:
            lx.command("select.element", layer=layer, type="polygon", mode="add", index=poly)

    def selectCollisionPolys(self):
        for poly in self.collision_poly_indices:
            lx.command("select.element", layer=layer, type="polygon", mode="add", index=poly)
            
    def selectAllPolys(self):
        self.selectRenderPolys()
        self.selectCollisionPolys()
        
    def eulerRotateTo (self, euler, pos=None):
        new_euler = -(euler[0] - self.euler[0]),\
                    -(euler[1] - self.euler[1]),\
                    -(euler[2] - self.euler[2])
        lx.out(euler)
        lx.out(self.euler)
        lx.out(new_euler)
        #lx.out("target: " + str(euler) + "\n current: " + str(self.euler)  + "\n rotation: " + str(new_euler))
        lx.eval("select.drop polygon")
        self.selectAllPolys()
        if pos:
            lx.eval("tool.set actr.auto on")
            lx.eval("tool.setAttr center.auto cenX " + str(pos[0]))
            lx.eval("tool.setAttr center.auto cenY " + str(pos[1]))
            lx.eval("tool.setAttr center.auto cenZ " + str(pos[2]))
        else:
            lx.eval("tool.set actr.origin on")
        rotateY(new_euler[0])
        rotateZ(new_euler[1])
        rotateX(new_euler[2])
        self.updateVecPos();

    def eulerUnRotateTo (self, euler, pos=None):
        new_euler = -(euler[0] - self.euler[0]),\
                    -(euler[1] - self.euler[1]),\
                    -(euler[2] - self.euler[2])
        lx.out(euler)
        lx.out(self.euler)
        lx.out(new_euler)
        #lx.out("target: " + str(euler) + "\n current: " + str(self.euler)  + "\n rotation: " + str(new_euler))
        lx.eval("select.drop polygon")
        self.selectAllPolys()
        lx.eval("tool.set actr.origin on")
        rotateX(new_euler[2], pos)
        rotateZ(new_euler[1])
        rotateY(new_euler[0])
        self.updateVecPos();
        # error("pause","pause")

    def getBBox (self):
        lx.out
        highestX = lowestX = self.render_vert_pos[0][0]
        highestY = lowestY = self.render_vert_pos[0][1]
        highestZ = lowestZ = self.render_vert_pos[0][2]
        for vertex_pos in self.render_vert_pos:
            if vertex_pos[0] > highestX : highestX = vertex_pos[0]
            if vertex_pos[1] > highestY : highestY = vertex_pos[1]
            if vertex_pos[2] > highestZ : highestZ = vertex_pos[2]
            if vertex_pos[0] < lowestX : lowestX = vertex_pos[0]
            if vertex_pos[1] < lowestY : lowestY = vertex_pos[1]
            if vertex_pos[2] < lowestZ : lowestZ = vertex_pos[2]
        
        return (highestX, highestY, highestZ),(lowestX, lowestY, lowestZ)
