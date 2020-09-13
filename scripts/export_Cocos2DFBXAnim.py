# python

import lx
import modoutil
import os
import shlex
import sys
import cPickle
import math


lx.eval("anim.setup on")

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

num_item = lx.eval("query sceneservice item.N ?")
for idx in range(num_item):
    if lx.eval("query sceneservice item.type ? " + str(idx)) == "locator":
        item_idx = lx.eval("query sceneservice item.id ? " + str(idx))
        name = lx.eval("query sceneservice item.name ? " + str(idx))
        xfrms = lx.eval("query sceneservice item.xfrmItems ? " + name)
        rot_zero = list()
        rot = list()
        for xfrm in xfrms:
            if lx.eval("query sceneservice item.type ? " + xfrm) == "rotation":
                xfrm_name = lx.eval("query sceneservice item.name ? " + xfrm)
                if "Rotation Zero" in xfrm_name:
                    rot_zero.append(xfrm)
                elif "Rotation" in xfrm_name:
                    rot.append(xfrm)
        if rot_zero[0] and rot[0]:
            for x in rot_zero,rot:
                lx.eval("query sceneservice item.name ? " + str(x[0]))
                num_channels = lx.eval("query sceneservice channel.N ?")
                val = [0,0,0]
                for channel_idx in range(num_channels):
                    channel_name = lx.eval("query sceneservice channel.name ? " + str(channel_idx))
                    channel_value = lx.eval("query sceneservice channel.value ? " + str(channel_idx))
                    if channel_name == "rot.X":
                        val[0] = float(channel_value)
                    elif channel_name == "rot.Y":
                        val[1] = float(channel_value)
                    elif channel_name == "rot.Z":
                        val[2] = float(channel_value)
                x.append(val)
            #lx.eval("channel.value 0.0 channel:{" + rot_zero[0] + ":rot.X}")
            #lx.eval("channel.value 0.0 channel:{" + rot_zero[0] + ":rot.Y}")
            #lx.eval("channel.value 0.0 channel:{" + rot_zero[0] + ":rot.Z}")
            #lx.eval("channel.value " + str(math.degrees(rot[1][0] + rot_zero[1][0])) + " channel:{" + rot[0] + ":rot.X}")
            #lx.eval("channel.value " + str(math.degrees(rot[1][1] + rot_zero[1][1])) + " channel:{" + rot[0] + ":rot.Y}")
            #lx.eval("channel.value " + str(math.degrees(rot[1][2] + rot_zero[1][2])) + " channel:{" + rot[0] + ":rot.Z}")
            lx.out(rot)
            lx.out(rot_zero)
            lx.eval("select.typeFrom item;pivot;center;edge;polygon;vertex;ptag false")
            lx.eval("select.subItem " + lx.eval("query sceneservice item.id ? " + str(idx)) + " set locator 0 0")

            lx.eval("tool.noChange")
            lx.eval("tool.doApply")
            lx.eval("tool.set TransformRotateItem on")
            lx.eval("tool.noChange")
            lx.eval("tool.doApply")
            lx.eval("tool.setAttr xfrm.transform comp true")
            lx.eval("tool.doApply")
            lx.eval("tool.set actr.pivot on")
            lx.eval("tool.doApply")

            #lx.eval("select.item " + lx.eval("query sceneservice item.id ? " + str(idx)) + " add")
            #lx.eval("tool.noChange")
            lx.eval("select.drop channel")
            #lx.eval("select.channel {" + rot[0] + ":rot.X} add")
            #lx.eval("select.channel {" + rot[0] + ":rot.Y} add")
            #lx.eval("select.channel {" + rot[0] + ":rot.Z} add")
            #lx.eval("select.channel {" + rot[0] + ":rot.X} add")
            #lx.eval("select.channel {" + rot[0] + ":rot.Y} add")
            #lx.eval("select.channel {" + rot[0] + ":rot.Z} add")
            #lx.eval("tool.doApply")
            
            lx.eval("tool.setAttr xfrm.transform RY " + str(math.degrees(rot[1][1] + rot_zero[1][1])))
            lx.eval("tool.setAttr xfrm.transform RX " + str(math.degrees(rot[1][0] + rot_zero[1][0])))
            lx.eval("tool.setAttr xfrm.transform RZ " + str(math.degrees(rot[1][2] + rot_zero[1][2])))

            lx.eval("tool.doApply")

            #lx.out("select.item " + lx.eval("query sceneservice item.id ? " + str(idx)))
            #lx.out("select.channel {" + rot[0] + ":rot.X} add")
            #lx.out("tool.setAttr xfrm.transform RZ " + str(math.degrees(rot[1][2] + rot_zero[1][2])))
            #lx.out("tool.setAttr xfrm.transform RX " + str(math.degrees(rot[1][0] + rot_zero[1][0])))
            #lx.out("tool.setAttr xfrm.transform RY " + str(math.degrees(rot[1][1] + rot_zero[1][1])))
            lx.eval("tool.set TransformRotateItem off")
            #lx.eval("tool.noChange")
            lx.eval("tool.doApply")
            lx.eval("transform.zero rotation")
            #lx.eval("tool.noChange")
            lx.eval("tool.doApply")
            sys.exit("LXe_SUCCESS")
            #lx.eval("select.item " + lx.eval("query sceneservice item.id ? " + str(idx)) + " remove")


         
            
            
        

#command = path + " " + filename
#os.system(command)
#os.system(scenedir + "fbx-conv.exe -a " + filename)
#os.system("fbx-conv.exe -a " + filename)





