#python 

import lx
import sys

def SetValue(args):
    if "value" not in args:
        args["value"] = ""
    lx.eval("channel.value " + args["value"] + " channel:{" + item + ":" + args["name"] +"}")


args = lx.args()

args = dict(map(str.strip, arg.split(':', 1)) for arg in args)

items = lx.evalN("query sceneservice selection ? " + args["itemtype"])

if items == None:
    sys.exit("LXe_SUCCESS")
for item in items:
    lx.eval("query sceneservice item.name ? " + item)

    # check if the channel already exists
    for i in range(lx.eval("query sceneservice channel.N ?")):
        if lx.eval("query sceneservice channel.name ? " + str(i)) == args["name"]:
            if "action" in args and args["action"] == "delete":
                lx.eval("channel.delete")
            else:
                SetValue(args)
            sys.exit("LXe_SUCCESS")

    lx.eval("channel.create item:" + item + " name:" + args["name"] + " type:" + args["type"])
    SetValue(args)