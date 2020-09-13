# python

import lx
import modoutil
import os
import shlex
import sys
import cPickle

#--------BEGIN MAIN----------#
    
args = lx.args()

platform = None
for arg in args:
    platform = arg

if lx.eval("query scriptsysservice userValue.isdefined ? pr_unityProjectDir"):
    unityProjDir = lx.eval("user.value pr_unityProjectDir ?")

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





