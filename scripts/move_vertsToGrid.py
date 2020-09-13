# python
# Author: Peter Respondek
# Takes your current selection and snaps vertices into the grid. Please note
# that it treats the grid exponent separately. For instance if you set a 16.5 grid
# it will set it to a 16 grid and then a 0.5 grid.

import lx
from math import modf

grid_size = 0

def error(titleString, errorString):
    lx.eval("dialog.setup error")
    lx.eval("dialog.title \"%s\"" % titleString)
    lx.eval("dialog.msg \"%s\"" % errorString)
    lx.eval("dialog.open")

args = lx.args()

if len(args) == 0:
    lx.eval("user.defNew name:gridSize life:momentary")
    lx.eval("user.def gridSize username {Grid Size}")
    lx.eval("user.def gridSize type float")
    lx.eval("user.value gridSize")
    grid_size = lx.eval("user.value gridSize ?")
    
else:
    for arg in args:    
        try:
            grid_size = float(arg)
        except:
            error("Invalid Number","This script takes floating point numbers only")
            sys.exit("LXe_FAILED")
            
# lx.out(grid_size)
lx.eval ("select.convert vertex")        
vertex_index_list = lx.eval("query layerservice verts ? selected")

if vertex_index_list == None:
    error("No Geometry", "No vertices found in selection.")
    sys.exit("LXe_FAILED")

grid_exp, grid_size = modf(grid_size)
m = lx.Monitor()
m.init(len(vertex_index_list))   

for vertex in vertex_index_list:
    expX = expY = expZ = 0
    X,Y,Z = lx.eval("query layerservice vert.wpos ? " + str(vertex))
    # lx.out("-------------------------")
    # lx.out(str(X) + "," + str(Y) + "," + str(Z))
    expX,X = modf(X)
    expY,Y = modf(Y)
    expZ,Z = modf(Z) 
    if (grid_exp != 0):
        expX = round(expX/grid_exp) * grid_exp
        expY = round(expY/grid_exp) * grid_exp
        expZ = round(expZ/grid_exp) * grid_exp
    else:
        expX = expY = expZ = 0
           
    # lx.out(str(expX) + "," + str(expY) + "," + str(expZ))

    if (grid_size != 0):
        X = (round (X/grid_size) * grid_size)
        Y = (round (Y/grid_size) * grid_size)
        Z = (round (Z/grid_size) * grid_size)

    X = X + expX
    Y = Y + expY
    Z = Z + expZ
    
    # lx.out(str(X) + "," + str(Y) + "," + str(Z))
    lx.command( "vert.move", vertIndex = vertex, posX = X, posY = Y, posZ = Z )
    m.step( 1 )   
