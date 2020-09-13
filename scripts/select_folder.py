#python

import lx

args = lx.args()

title = args[0]
title = '"' + title + '"'

lx.eval( "dialog.setup dir" )
lx.eval( "dialog.title " + title )
lx.eval( "dialog.result ok" )
try:
    lx.eval( "dialog.open" )
    result = lx.eval( "dialog.result ?" )
except:
    sys.exit("LXe_ABORT")

if lx.eval( "query scriptsysservice userValue.isDefined ? " + args[1] ):
    lx.eval( "user.value " + args[1] + " \"" + result + "\"" )
    