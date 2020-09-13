#python

import lx
import lxu.select
import plistlib
import modoutil
import sys
import os
import math

def expandList(plist, size):
    while len(plist) < size:
        plist.append(["","",""])

def writeSpactial(name,plist):
    plist.append(lx.eval("query sceneservice item.name ? " + name))
    plist.append(lx.eval("query sceneservice item.pos ? " + name))
    plist.append([math.degrees(x) for x in lx.eval("query sceneservice item.rot ? " + name)])
    plist.append(lx.eval("query sceneservice item.scale ? " + name))
    
def writeMesh(name,plist):
    mesh_entry = list()    
    item_type = lx.eval("query sceneservice item.type ? " + child)
    writeSpactial(name,mesh_entry)

    if item_type == "meshInst":
        lx.eval("select.item item:" + name + " mode:set")
        lx.eval("select.itemSourceSelected")
        name = lx.eval("item.name ?")
        
    mesh_entry.append(lx.eval("query layerservice layer.name ? " + name))
    
    lightmap = ""
    shader = ""
    pose = ""
    animation = False
    shader_values = list()
    vmaps = set()
    for vmap in lx.evalN("query layerservice vmaps ? texture"):
        vmap_name = lx.eval("query layerservice vmap.name ? " + vmap)
        for poly in lx.evalN("query layerservice polys ? all"):
            for x in lx.eval("query layerservice poly.vmapValue ? " + poly):
                if x != 0:
                    vmaps.add(vmap_name)
    for vmap in vmaps:
        if "lightmap" in vmap:
            lightmap = vmap
            break

    for i in range(lx.eval("query sceneservice channel.N ?")):
        channel_name = lx.eval("query sceneservice channel.name ? " + str(i))
        channel_value = lx.eval("query sceneservice channel.value ? " + str(i))
        shader_value = list()
        if channel_name == "Shader":
            shader = channel_value
        elif channel_name == "Pose":
            pose = channel_value
        elif channel_name == "Animation":
            animation = channel_value
        elif "ShaderValue" in channel_name:
            idx = int(channel_name[11:]) - 1
            expandList(shader_values, idx + 1)
            shader_value.append(channel_value)
            shader_values[idx][2] = shader_value
        elif "ShaderName" in channel_name:
            idx = int(channel_name[10:]) - 1
            expandList(shader_values, idx + 1)
            shader_values[idx][0] = channel_value
        elif "ShaderType" in channel_name:
            idx = int(channel_name[10:]) - 1
            expandList(shader_values, idx + 1)
            shader_values[idx][1] = channel_value
        
    mesh_entry.append(lightmap)
    mesh_entry.append(shader)
    mesh_entry.append(shader_values)

    if animation:
        mesh_entry.append(pose)
        plist['SkelMeshes'].append(mesh_entry)
    else:
        plist['StaticMeshes'].append(mesh_entry)

def writeCamera(name,plist):
    camera_entry = [name]
    camera_entry.append(lx.eval("query sceneservice item.pos ? " + name))
    camera_entry.append([math.degrees(x) for x in lx.eval("query sceneservice item.rot ? " + name)])

    fov = "35"
    near_p = "500"
    far_p = "10000"

    for i in range(lx.eval("query sceneservice channel.N ?")):
        channel_name = lx.eval("query sceneservice channel.name ? " + str(i))
        channel_value = lx.eval("query sceneservice channel.value ? " + str(i))
        spline_name = ""
        
        if channel_name == 'spline':
            spline_name = channel_value
        elif channel_name == 'FOV':
            fov = channel_value
        elif channel_name == 'NearP':
            near_p = channel_value
        elif channel_name == 'FarP':
            far_p = channel_value
            
    if spline_name:
        for i in lx.evalN("query layerservice layers ? all"):
            if spline_name == lx.eval("query layerservice layer.name ? " + str(i)):
                spline_entry = [spline_name]
                for poly in lx.evalN("query layerservice polys ? all"):
                    if lx.eval("query layerservice poly.type ? " + str(poly)) == 'curve':
                        for vert in lx.evalN("query layerservice poly.vertList ? " + str(poly)):
                            spline_entry.append(lx.eval("query layerservice vert.pos ? " + str(vert)))
        if spline_entry:
            plist['Splines'].append(spline_entry)

    camera_entry.append([fov, near_p, far_p])
    camera_entry.append(spline_name)
    plist['Cameras'].append(camera_entry)
 
# get a channel object

def writeSprite(name,plist):
    sprite_entry = list()
    writeSpactial(name,sprite_entry)
    texture = ""
    
    for i in range(lx.eval("query sceneservice channel.N ?")):
        channel_name = lx.eval("query sceneservice channel.name ? " + str(i))
        channel_value = lx.eval("query sceneservice channel.value ? " + str(i))
        if channel_name == "Texture":
            texture = channel_value
    sprite_entry.append(texture)
    plist['Sprites'].append(sprite_entry)


scenedir = lx.eval("query sceneservice scene.file ? current")
if not scenedir:
    modoutil.error("Bad file","Save file before exporting")
    
scenename = lx.eval("query sceneservice scene.name ? current")
scenedir = scenedir[:-len(scenename)]
layer_name = lx.eval("query layerservice layer.name ? selected")
lx.out(layer_name)

item_name = lx.evalN("item.name ?")
for item in item_name:
    item_type = lx.eval("query sceneservice item.type ? \"" + item+ "\"")
    if item_type == "groupLocator":
        item_name = item
        break
    
lx.out(item_name)
filename = scenedir + item_name + ".plist"

plist = dict()
plist['Location'] = list()
plist['Splines'] = list()
plist['Cameras'] = list()
plist['StaticMeshes'] = list()
plist['SkelMeshes'] = list()
plist['Sprites'] = list()

location = ["","",""]
for i in range(lx.eval("query sceneservice channel.N ?")):
        channel_name = lx.eval("query sceneservice channel.name ? " + str(i))
        channel_value = lx.eval("query sceneservice channel.value ? " + str(i))
        if channel_name == "Location":
            location[0] = channel_value
        elif channel_name == "Area":
            location[1] = channel_value
        elif channel_name == "Time":
            location[2] = channel_value
plist['Location'] = location

for child in lx.eval("query sceneservice item.children ? " + item_name):
    item_type = lx.eval("query sceneservice item.type ? " + child)
    lx.out(item_type)
    if item_type == "mesh" or item_type == "meshInst":
        writeMesh(child,plist)
    elif item_type == "camera":
        writeCamera(child,plist)
    elif item_type == "locator":
        writeSprite(child,plist)
        
if os.path.exists(filename):
    os.remove(filename)
plist_file = open(filename, 'w+')
plistlib.writePlist(plist, plist_file)

plist_file.flush()
plist_file.close()

sys.exit("LXe_SUCCESS")
