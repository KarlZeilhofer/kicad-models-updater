

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
from KicadCommon import *
import os
import argparse


parser = argparse.ArgumentParser(prog="kicad-update-3d-models",
                                    description="Gets paths for 3D models from the used footrints and updates it in "
                                                "the .kicad_pcb file"
                                                "without changing any other properties in the layout. ")

defaultConfigPath = os.path.expanduser('~/.config/kicad')
parser.add_argument("-c", "--configpath", dest='cpath', default=defaultConfigPath,
                    help='system wide config path, where kicad_comman and fp-lib-table can be found. '
                         'Default is ' + defaultConfigPath)

parser.add_argument("-p", "--projectpath", dest='ppath', default=os.getcwd(),
                    help='path to kicad project, where .kicad_pcb and option fp-lib-table can be found. '
                         'Default is the current working directory')

parser.add_argument("-f", "--pcbfile", dest='pcbfile', default='',
                    help='.kicad_pcb file to be modified. Default is the .kicad_pcb in the project path.')

args = parser.parse_args();

print('running ' + parser.prog + ' ...')

if not os.path.exists(args.cpath):
    print("Error: config path does not exist: " + args.cpath)
    exit()
print('cpath: ' + args.cpath)


if not os.path.exists(args.ppath):
    print("Error: project path does not exist: " + args.ppath)
    exit()

print('ppath: ' + args.ppath)

if args.pcbfile:
    if not os.path.isfile(args.pcbfile):
        print("Error: specified .kicad_pcb file doesn't exist: " + args.pcbfile)
        exit()
    else:
        args.pcbfile = os.getcwd() + os.path.sep + args.pcbfile
else: # search for a .kicad_pcb file
    filesAndDirs = os.listdir(args.ppath)
    count = 0
    for i in filesAndDirs:
        if i.endswith('.kicad_pcb'):
            args.pcbfile = i
            count += 1
    if not args.pcbfile:
        print("Error: Cannot find any .kicad_pcb file in project path " + args.ppath)
        exit()
    if count > 1:
        print("Error: Found multiple .kicad_pcb files in project path " + args.ppath + "\nPlease use -f flag")
        exit()

    if not os.path.isabs(args.pcbfile):
        args.pcbfile = args.ppath + os.path.sep + args.pcbfile

print('pcbfile: ' + args.pcbfile)


print()



# read environment variables from kicad_common
kcc = KicadCommon(args.cpath)
print(kcc)



pcb = Layout(args.pcbfile)
# pcb.mod.printTree()

pcbFP = pcb.getFootprints()
# if pcbFP:
#     for w in pcbFP:
#         print(w, end=' ')
#         print(w.getValue())


fplibtableLocal = None
if os.path.isfile('fp-lib-table'): # check for local fp-lib-table
    fplibtableLocal = LibTable("fp-lib-table")

fplibtableGlobal = LibTable(args.cpath + os.path.sep + "fp-lib-table")
list = fplibtableGlobal.getLibNames()
# if list:
#     for w in list:
#         print(w.getValue(), end=', ')
#         print(kcc.expandPath(fplibtableGlobal.getUri(w)))
#

