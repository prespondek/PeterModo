# python
# Title: Parts to Layers
# Author: Peter Respondek

# Makes a new layer for any selected parts and moves the geo. 

import lx

def error(titleString, errorString):
    lx.eval("dialog.setup error")
    lx.eval("dialog.title \"%s\"" % titleString)
    lx.eval("dialog.msg \"%s\"" % errorString)
    lx.eval("dialog.open")

num_layers = lx.eval("query layerservice layer.N ? all")
fg = lx.eval("query layerservice layers ? fg")
parent = lx.eval("query layerservice layer.parent ? " + str(fg))
layer_id = lx.eval("query layerservice layer.id ? fg")

layers_list=[]
for i in range(1,num_layers+1):
    lx.out(lx.eval("query layerservice layer.name ? " + str(i)))
    layers_list.append(lx.eval("query layerservice layer.name ? " + str(i)))

num_parts = lx.eval("query layerservice part.N ? all")
parts_list=set()
lx.eval("query layerservice layers ? fg")
try:
    poly_index_list = set(lx.eval("query layerservice polys ? selected"))
except:
    try:
        poly_index_list = set(lx.eval("query layerservice polys ? all"))
    except:
        error("Bad selection","No geometry in selected layer")
        sys.exit("LXe_ABORT")


for poly in poly_index_list:
    parts_list = parts_list | set([lx.eval("query layerservice poly.part ? " + str(poly))])
parts_list = parts_list - set([None,"Default",""])
for part in parts_list:
    lx.command("select.layer", number=fg, mode=set)
    lx.eval("select.drop polygon")
    lx.eval("select.polygon add part face " + str(part))
    lx.eval("cut")
    if part not in layers_list:
        lx.out(part)
        lx.command("item.create", type="mesh", name=str(part))
        new_layer_index = lx.eval("query layerservice layer.index ? fg")
        new_layer_id = lx.eval("query layerservice layer.id ? " + str(new_layer_index))
        lx.eval("item.parent " + new_layer_id + " " + str(parent) + " inPlace:1")
        num_layers += 1
        layers_list=[]
        for i in range(1,num_layers):
            layers_list.append(lx.eval("query layerservice layer.name ? " + str(i)))
    else:
        lx.out("Boo")
    lx.out(layers_list)
    for i in range(0,num_layers-1):
        lx.out(i)
        if layers_list[i] == part:
            lx.command("select.layer", number=i, mode=set)
    lx.eval("paste")
        
    
    

