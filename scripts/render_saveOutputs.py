#python

import lx
import os
import sys

filepath = lx.eval("query sceneservice scene.file ? current")
if len(filepath) == 0:
    error("Invaild Save File","Save your file before running this script")
    sys.exit("LXe_FAILED")

dir = os.path.dirname(filepath)
scenename = os.path.splitext(lx.eval("query sceneservice scene.name ? current"))[0]

lx.out(dir)
if lx.eval("query scriptsysservice userValue.isDefined ? pr_render_saveOutputsDir") and \
    lx.eval("query scriptsysservice userValue.isSet ? pr_render_saveOutputsDir"):
    dir = lx.eval("user.value pr_render_saveOutputsDir ?")

dir += "\\"

convention = ["",""]
layerindex = str(lx.eval("query layerservice layers ? main"))
layername = lx.eval("query layerservice layer.name ? " + layerindex)
layerid = lx.eval("query layerservice layer.id ? " + layerindex)

outputs = []
conventions = []
for i in range(lx.eval("query sceneservice item.N ?")):
    name = lx.eval("query sceneservice item.name ? "+str(i))
    if lx.eval("query sceneservice isType ? renderOutput") and lx.eval("query sceneservice channel.value ? 0") == "1":
        outputs.append(name)
        convention = ["",""]
        for j in range(lx.eval("query sceneservice channel.N ?")):
            channel = lx.eval("query sceneservice channel.name ? " + str(j))
            if channel == "FilePrefix": 
                convention[0] = lx.eval("query sceneservice channel.value ? " + str(j))
            elif channel == "FilePostfix":
                convention[1] = lx.eval("query sceneservice channel.value ? " + str(j))
        if convention == ["",""]:
            convention[1] = name
        conventions.append(convention)

lx.eval("render filename:" + dir + " format:PNG options:0")
for i in range(len(outputs)):
    filename = dir + scenename + "_" + conventions[i][0] + layername + conventions[i][1] + ".png"
    if os.path.exists(filename): 
        os.remove(filename)
    os.rename(dir + outputs[i] + "0000.png", filename)
