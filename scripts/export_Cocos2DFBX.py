# python

import lx
import modoutil
import os
import shlex
import sys
import cPickle

def writeMesh(name):
    layer_name = lx.eval("query layerservice layer.name ? " + name)
    lx.eval("select.item item:" + name + " mode:set")
    vert_idxs = lx.evalN("query layerservice verts ? all")
    vert_pos = list()
    vert_normal = list()
    for idx in vert_idxs:
        vert_pos.append(lx.eval("query layerservice vert.pos ? " + idx))
        vert_normal.append(lx.eval("query layerservice vert.normal ? " + idx))

    textures = dict()
    materials = dict()
    for material_idx in lx.evalN("query layerservice materials ?"):
        material_name = lx.eval("query layerservice material.name ? " + material_idx)
        material_textures = lx.evalN("query layerservice material.textures ? " + material_idx)
        materials[material_name] = material_textures
    for texture_idx in lx.evalN("query layerservice textures ? all"):
        texture_name = lx.eval("query layerservice texture.id ? " + texture_idx)
        if lx.eval("query layerservice texture.type ? " + texture_idx) == 'imageMap':
            texture_clip = lx.eval("query layerservice texture.clipFile ? " + texture_idx)
            if 'iOS' in platform:
                if '.pvr.ccz' in material_name:
                    texture_clip = texture_clip[:-4]
                    texture_clip = texture_clip + ".pvr.ccz"
            if 'android' in platform:
                if '.pkm' in material_name:
                    texture_clip = texture_clip[:-4]
                    texture_clip = texture_clip + ".pkm"
            texture_uv_idx = lx.eval("query layerservice texture.uvMap ? " + texture_idx)
            if texture_uv_idx:
                texture_uv = lx.eval("query layerservice vmap.name ? " + str(texture_uv_idx))
            textures[texture_name] = [texture_clip, texture_uv]
        elif lx.eval("query layerservice texture.type ? " + texture_idx) == 'advancedMaterial':
            lx.eval("select.subItem " + texture_name + " set textureLayer;")
            lx.eval("item.channel advancedMaterial$smAngle 180.0")

    poly_idxs = lx.evalN("query layerservice polys ? all")
    poly_verts = list()
    poly_materials = list()
    for idx in poly_idxs:
        poly_materials.append(lx.eval("query layerservice poly.material ? " + idx))
        poly_verts.append(lx.eval("query layerservice poly.vertList ? " + idx))

    vmaps = lx.eval("query layerservice vmaps ? all")

    uvmaps =            list()
    colormaps =         list()

    for vmap in vmaps:

        vmap_type = lx.eval("query layerservice vmap.type ? " + vmap)
        vmap_name = lx.eval("query layerservice vmap.name ? " + vmap)
        
        if "texture" == vmap_type:
            uvmap_values = list()
            active_uv = False
            for idx in poly_idxs:
                uvmap_value = lx.eval("query layerservice poly.vmapValue ? " + idx)
                uvmap_values.append(uvmap_value)
                for val in uvmap_value:
                    if val > 0.0:
                        active_uv = True
            if active_uv:
                lx.out(uvmap_values)
                uvmaps.append((vmap_name, uvmap_values))
                
        elif "rgb" == vmap_type or "rgba" == vmap_type:
            colormap_values = list()
            active_color = False
            for idx in vert_idxs:
                colormap_value = lx.eval("query layerservice vert.vmapValue ? " + idx)
                if not colormap_value:
                    colormap_value = (0.0,0.0,0.0)
                colormap_values.append(colormap_value)
                for val in colormap_value:
                        if val > 0.0:
                            active_color = True
            if active_color:
                colormaps.append((vmap_name,colormap_values))
                
    filename = scenedir + layer_name + ".fbx"
    lx.out(materials)
    lx.out(textures)
    for uvmap in uvmaps:
        lx.out(uvmap)


    lx.out(len(vert_normal))
    data = {'name':             layer_name, \
            'verts':            vert_pos,\
            'normals':          vert_normal,\
            'polys':            poly_verts,\
            'polymaterials':    poly_materials,\
            'uvmaps':           uvmaps,\
            'colormaps':        colormaps, \
            'materials':        materials, \
            'textures':         textures} 
    lx.out(colormaps)
    if os.path.exists(filename):
        os.remove(filename)
    fbx_file = open(filename, 'w+')
    cPickle.dump(data,fbx_file)
    fbx_file.flush()
    fbx_file.close()

    path = lx.eval("query platformservice path.path ? kits")
    path = path + "\petermodo\scripts\make_cocos2DFBX.py"
    if not os.path.exists(path):
        modoutil.error("Bad Path", "Can't find FBX Materials Script")
        sys.exit("LXe_ABORT")
    command = path + " " + filename
    os.system(command)
    os.system(scenedir + "fbx-conv.exe -a " + filename)

#--------BEGIN MAIN----------#
    
args = lx.args()

platform = None
for arg in args:
    platform = arg

scenedir = lx.eval("query sceneservice scene.file ? current")
if not scenedir:
    modoutil.error("Bad file","Save file before exporting")
    
scenename = lx.eval("query sceneservice scene.name ? current")
scenedir = scenedir[:-len(scenename)]
layer_name = lx.eval("query layerservice layer.name ? main")

#if not layer_name:
#    modoutil.error("Bad Selection", "Layer not selected")
#    sys.exit("LXe_ABORT")

item_name = lx.evalN("item.name ?")
for item in item_name:
    lx.out(item)
    item_type = lx.eval("query sceneservice item.type ? " + item)
    if item_type == "groupLocator":
        item_name = item
        for child in lx.eval("query sceneservice item.children ? " + item_name):
            item_type = lx.eval("query sceneservice item.type ? " + child)
            lx.out(item_type)
            if item_type == "mesh":
                writeMesh(child)
                
    elif item_type == "mesh":
        writeMesh(item)
        
sys.exit("LXe_ABORT")
#os.system("fbx-conv.exe -a " + filename)





