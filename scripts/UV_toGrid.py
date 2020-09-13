#python

import lx
import sys
import time


gridSize = 0.25
objectSize = 64
    
if lx.eval("query scriptsysservice userValue.isdefined ? pr_gridUVObjectSize"):
    objectSize = lx.eval("user.value pr_gridUVObjectSize ?")

if lx.eval("query scriptsysservice userValue.isdefined ? pr_gridUVGridSize"):
    gridSize = lx.eval("user.value pr_gridUVGridSize ?")

layers = lx.eval("query layerservice layers ? all")
for layer in layers:
    

