#python
#Author:        Peter Respondek
#Title:         Export to VMF format
#Descrition:    Exports geometry to VMF format for use in Hammer editor. (Valve)
#               Use at your own risk


import lx
import os
import modoutil
import modomath

def getDominateNormal(normal):
    best_axis = "Y"
    if abs(normal[0]) > abs(normal[1]):
        if abs(normal[0]) > abs(normal[2]):
            best_axis = "X"
    elif abs(normal[2]) > abs(normal[0]):
        if abs(normal[2]) > abs(normal[1]):
            best_axis = "Z"
    return best_axis


fg = lx.eval("query layerservice layers ? main")
uvmap = lx.eval("query layerservice vmaps ? selected")
for vmap in lx.eval("query layerservice vmaps ? all"):
    vmap_idx = lx.eval("query layerservice vmap.index ? " + vmap)
    if lx.eval("query layerservice vmap.type ? " + vmap) == "texture":
        uvmap = lx.eval("query layerservice vmaps ? " + vmap_idx)
    
counter = 2
distance = 32
extrude = False

args = lx.args()

for arg in args:
    if arg == "extrude":
        extrude = True

if not lx.eval("query scriptsysservice userValue.isdefined ? vmffilepath"):
    lx.eval("user.defNew name:vmffilepath type:string life:temporary")
    lx.eval("user.value vmffilepath \"C:\Program Files (x86)\Steam\steamapps\\\"")
lx.out(lx.eval("user.value vmffilepath ?"))

lx.eval("dialog.setup fileSave")
lx.eval("dialog.title \"Map Save Location...\"")
lx.eval("dialog.fileTypeCustom vmf \"Valve Map Format\" \"*.vmf\" vmf")
lx.eval("dialog.result \"" + lx.eval("user.value vmffilepath ?") + "\"")
try:
    lx.eval("dialog.open")
except:
    sys.exit("LXe_ABORT")
    
map_file = lx.eval("dialog.result ?")
lx.eval("user.defDelete name:vmffilepath")
lx.eval("user.defNew name:vmffilepath type:string life:temporary")
lx.eval("user.value vmffilepath \"" + map_file + "\"")

if extrude:
    try:
        lx.eval("user.defNew name:threshold type:integer life:momentary")
        lx.eval("user.def threshold username {Extrude Distance}")
        lx.eval("user.value threshold")
    except:
        sys.exit("LXe_ABORT")

    distance = lx.eval("user.value threshold ?")

lx.eval("select.typeFrom polygon")
polys = lx.eval("query layerservice polys ? selected")
if not polys:
    lx.eval("select.all")
if not polys:
    modoutil.error("No Geometry","No polygons in layer")
    sys.exit("LXe_ABORT")

lx.eval("hide.Unsel")
    

lx.eval("tool.set xfrm.quantize on")
lx.eval("tool.attr xfrm.quantize X 1.0")
lx.eval("tool.attr xfrm.quantize Y 1.0")
lx.eval("tool.attr xfrm.quantize Z 1.0")
lx.eval("tool.doApply")
lx.eval("tool.set xfrm.quantize off")

if extrude:
    lx.eval("vert.split")

tmp_file = open (map_file, 'w')

tmp_file.write ("versioninfo\n{\n\t\"editorversion\" \"400\"\n\t\"editorbuild\" \"5685\"\n\t\"mapversion\" \"34\"\n\t\"formatversion\" \"100\"\n\t\"prefab\" \"0\"\n}")
tmp_file.write ("\nvisgroups\n{\n}")
tmp_file.write ("\nviewsettings\n{\n\t\"bSnapToGrid\" \"1\"\n\t\"bShowGrid\" \"1\"\n\t\"bShowLogicalGrid\" \"0\"\n\t\"nGridSpacing\" \"32\"\n\t\"bShow3DGrid\" \"0\"\n}")
tmp_file.write ("\nworld\n{\n\t\"id\" \"1\"\n\t\"mapversion\" \"34\"\n\t\"classname\" \"worldspawn\"\n\t\"detailmaterial\" \"detail/detailsprites\"\n\t\"detailvbsp\" \"detail.vbsp\"\n\t\"maxpropscreenwidth\" \"-1\"\n\t\"musicpostfix\" \"Waterfront\"\n\t\"skyname\" \"sky_l4d_rural02_hdr\"\n\t\"maxblobcount\" \"250\"")

while polys:
    poly = polys[0]
    counter+=1
    
    tmp_file.write ("\n\tsolid\n\t{")
    tmp_file.write ("\n\t\t\"id\" \"" + str(counter) + "\"")
    lx.command("select.element", layer=fg, type="polygon", mode="set", index=poly)
    normal = lx.eval("query layerservice poly.normal ? " + str(poly))
    best_normal = getDominateNormal(normal)

    if extrude:
        
        current_distance = distance
        if best_normal == "X" and normal[0] > 0:
            current_distance = -current_distance
        if best_normal == "Y" and normal[1] > 0:
            current_distance = -current_distance
        if best_normal == "Z" and normal[2] > 0:
            current_distance = -current_distance
            
        lx.eval("tool.set *.extrude on")
        if best_normal == "X":
            lx.eval("tool.setAttr poly.extrude shiftX " + str(current_distance))
        else:
            lx.eval("tool.setAttr poly.extrude shiftX 0.0")
        if best_normal == "Y":
            lx.eval("tool.setAttr poly.extrude shiftY " + str(current_distance))
        else:
            lx.eval("tool.setAttr poly.extrude shiftY 0.0")
        if best_normal == "Z":
            lx.eval("tool.setAttr poly.extrude shiftZ " + str(current_distance))
        else:
            lx.eval("tool.setAttr poly.extrude shiftZ 0.0")
        lx.eval("tool.doApply")
        lx.eval("tool.set *.extrude off")
        
    lx.eval("select.connect")
    
    extruded_polys = lx.eval("query layerservice polys ? selected")
    for extruded_poly in extruded_polys:
        # get all the data I want
        verts = lx.eval("query layerservice poly.vertList ? " + str(extruded_poly))
        verts_pos = [lx.eval("query layerservice vert.pos ? " + str(vert)) for vert in verts]
        edge_vecs = [modomath.vecSub(verts_pos[i],verts_pos[j]) for i,j in zip(range(len(verts_pos))[0::1] + [len(verts_pos)-1], \
                                                                               range(len(verts_pos))[1::1] + [0])]
        edge_dist = [modomath.vecNorm(x) for x in edge_vecs]
        edge_norms = [modomath.vecNormalized(x) for x in edge_vecs]
        uvs = lx.eval("query layerservice poly.vmapValue ? " + str(extruded_poly))
        uvs = zip(uvs[0::2], uvs[1::2])
        uv_vecs = [modomath.vecSub(uvs[i],uvs[j]) for i,j in zip(range(len(uvs))[0::1] + [len(uvs)-1], range(len(uvs))[1::1] + [0])]
        #uv_norms = [modomath.vecNormalized(x) for x in uv_vecs]
        uv_dist = [modomath.vecNorm(x) for x in uv_vecs]
        uv_angles = [modomath.vecAngle(*x) for x in uv_vecs]

        # in effect checks if the some of all angles are not equal to 360 polygon is non convex
        if reduce(lambda i,j:i-j, uv_angles) != 0:
            lx.out("Non Convex polygon detected")
            continue
        lx.eval("query layerservice poly.vertList ? " + str(poly))
        counter+=1
        tmp_file.write ("\n\t\tside\n\t\t{")
        tmp_file.write ("\n\t\t\t\"id\" \"" + str(counter) + "\"")
        tmp_file.write ("\n\t\t\t\"plane\" \"")
        for i in (0,2,1):
            tmp_file.write ("(")
            vert_pos = lx.eval("query layerservice vert.pos ? " + str(verts[i]))
            tmp_file.write (str(round(vert_pos[0],3)) + " " + str(round(-vert_pos[2],3)) + " " + str(round(vert_pos[1],3)))
            tmp_file.write (")")
            if i != 2:
                tmp_file.write (" ")
        tmp_file.write ("\"")
        tmp_file.write ("\n\t\t\t\"material\" \"TOOLS/TOOLSNODRAW\"")
        tmp_file.write ("\n\t\t\t\"uaxis\" \"[")
        extruded_normal = lx.eval("query layerservice poly.normal ? " + str(extruded_poly))

        # I determine the best vector by looking for how many are the same.
        #edge_norms = [tuple(map(lambda i:round(abs(i),4), edge_norm)) for edge_norm in edge_norms]
        #edge_dupes = [(edge_norms.count(edge_norm),edge_norm) for edge_norm in set(edge_norms)]
        #best_vec = max(edge_dupes)
        #lx.out(best_vec)
        
        #lx.out(edge_dupes)
        
        longest_edge = modoutil.getLongestEdge(extruded_poly)
        #longest_vector = modomath.vecNormalized(lx.eval("query layerservice edge.vector ? " + str(longest_edge[0]) + "," + str(longest_edge[1])))
        longest_vector = modomath.vecNormalized(modomath.vecSub(lx.eval("query layerservice vert.pos ? " + str(longest_edge[0])), \
                                                                lx.eval("query layerservice vert.pos ? " + str(longest_edge[1]))))
        longest_vector = (longest_vector[0],longest_vector[1],longest_vector[2])
        cross_vector = modomath.vecCrossProduct(longest_vector,extruded_normal)
        for i in (0,2,1):
           tmp_file.write (str(round(longest_vector[i],6)) + " ")
        tmp_file.write ("0] 0.25\"")
        tmp_file.write ("\n\t\t\t\"vaxis\" \"[")
        for i in (0,2,1):
           tmp_file.write (str(round(cross_vector[i],6)) + " ")
        tmp_file.write ("0] 0.25\"")
        tmp_file.write ("\n\t\t\t\"rotation\" \"0\"")
        tmp_file.write ("\n\t\t\t\"lightmapscale\" \"16\"")
        tmp_file.write ("\n\t\t\t\"smoothing_groups\" \"0\"")
        tmp_file.write ("\n\t\t}")
    tmp_file.write ("\n\t\teditor\n\t\t{\n\t\t\t\"color\" \"0 222 239\"\n\t\t\t\"visgroupshown\" \"1\"\n\t\t\t\"visgroupautoshown\" \"1\"\n\t\t}\n\t}")
    lx.eval("select.connect")
    lx.eval("delete")
    try:
        lx.eval("!!select.all")
    except:
        break
    polys = lx.eval("query layerservice polys ? selected")
    
tmp_file.write ("\n}\ncameras\n{\n\t\"activecamera\" \"-1\"\n}\ncordons\n{\n\t\"active\" \"0\"\n}")

tmp_file.flush()
os.fsync(tmp_file.fileno())
tmp_file.close()

#subprocess.call("notepad " + map_file, shell=True)

sys.exit("LXe_ABORT")
                
