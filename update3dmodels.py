

# This script updates the 3D models in a kicad_pcb file.
# Therefore it fetches all the used footprints from their respective library,
# reads out their model record, and writes this into the kicad_pcb file.
# Note: this can also be done by the GUI (at least with KiCad 4 and later), but
#   there also the location and size of the labels is reset, which is probably not
#   what the user inteded, if he only wants to reload the paths to the 3D models.

# (c) 2018 by Karl Zeilhofer, www.team14.at

# License: Public Domain

from Layout import *
from LibTable import *

pcb = Layout("test.kicad_pcb")
# pcb.mod.printTree()
pcbFP = pcb.getFootprints()
if pcbFP:
    for w in pcbFP:
        print(w, end=' ')
        print(w.getParentList()[1])


fplibtableGlobal = LibTable("/home/karl/.config/kicad/fp-lib-table")
list = fplibtableGlobal.getLibNames()
if list:
    for w in list:
        print(w.getValue())

