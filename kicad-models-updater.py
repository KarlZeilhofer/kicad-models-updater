#!/usr/bin/python3


# kicad-models-updater
# updates a KiCad PCB file, if the footprint libs have been changed
# Copyright (C) 2018 Karl Zeilhofer, www.team14.at
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.




# This script updates the 3D models in a kicad_pcb file.
# Therefore it fetches all the used pcbFootprints from their respective library,
# reads out their model record, and writes this into the kicad_pcb file.
# Note: this can also be done by the GUI (at least with KiCad 4 and later), but
#   there also the location and size of the labels is reset, which is probably not
#   what the user intended, if he only wants to reload the paths to the 3D models.


# License: Public Domain

from Layout import *
from LibTable import *
from KicadCommon import *
import os
import argparse
import platform



class App:
    def __init__(self):
        self.defaultConfigPath = ''
        if 'linux' in platform.system().lower():
            self.defaultConfigPath = os.path.expanduser('~/.config/kicad') # Linux: ~/.config/kicad
        elif 'win' in platform.system().lower():
            self.defaultConfigPath = os.path.join(os.getenv('APPDATA'), '\\kicad') # Windows: %APPDATA%\kicad
        elif  'mac' in platform.system().lower() or 'osx' in platform.system().lower():
            self.defaultConfigPath = os.path.expanduser('$HOME/Library/Preferences/kicad') # macOS: $HOME/Library/Preferences/kicad
        else:
            print("Warning: cannot identify operating system, needed for default config path")

        self.args = None # object from argument parser
        self.kcc = None # object of Kicad Common
        self.pcbFootprints = []  # list of Footprint objects
        self.usedFpSExpr = {}  ## Dict[str, SExpressionModifier]
        self.fpLibs = {}  # lib-name -> lib-path
        self.pcb = None

    def run(self):
        self.parseArguments()
        self.readEnvironmentVariables()
        self.readFootprintLibraryTables()
        self.readPcbFile()
        self.loadNeededFootprintFiles()
        self.modifyPcbData()
        self.writePcbFile()

    def parseArguments(self):
        #######################################################################################################################
        #                                  PARSE ARGUMENTS                                                                    #
        #######################################################################################################################
        parser = argparse.ArgumentParser(prog="kicad-models-updater",
                                            description="Gets paths for 3D models from the used footrints and updates it in "
                                                        "the .kicad_pcb file "
                                                        "without changing any other properties in the layout. ",
                                         epilog="GitHub: https://github.com/KarlZeilhofer/kicad-models-updater"
                                         )


        parser.add_argument("-c", "--configpath", dest='cpath', default=self.defaultConfigPath,
                            help='system wide config path, where kicad_comman and fp-lib-table can be found. '
                                 'Default is ' + self.defaultConfigPath)

        parser.add_argument("-p", "--projectpath", dest='ppath', default=os.getcwd(),
                            help='path to kicad project, where .kicad_pcb and optional fp-lib-table can be found. '
                                 'Default is the current working directory')

        parser.add_argument("-f", "--pcbfile", dest='pcbfile', default='',
                            help='.kicad_pcb file to be modified. Default is the .kicad_pcb in the project path. \n'
                                 'The --projectpath is overridden by a given --pcbfile')

        parser.add_argument("-o", "--output", dest='outputfile', default='',
                            help='.kicad_pcb file to write the modified PCB file to. Default is the input file, see --pcbfile'
                                 '\nUse this option, if you do not want to overwrite the original file')

        self.args = parser.parse_args();

        print('running ' + parser.prog + ' ...')

        if not os.path.exists(self.args.cpath):
            print("Error: config path does not exist: " + self.args.cpath)
            exit()
        print('cpath: '.ljust(20, ' ') + self.args.cpath)


        if not os.path.exists(self.args.ppath):
            print("Error: project path does not exist: " + self.args.ppath)
            exit()

        if self.args.pcbfile:
            if not os.path.isfile(self.args.pcbfile):
                print("Error: specified .kicad_pcb file doesn't exist: " + self.args.pcbfile)
                exit()
            else:
                self.args.pcbfile = os.getcwd() + os.path.sep + self.args.pcbfile
                self.args.ppath = os.path.dirname(self.args.pcbfile)
                print("Info: overriding project path with that from given PCB file")

        else: # search for a .kicad_pcb file
            filesAndDirs = os.listdir(self.args.ppath)
            count = 0
            for i in filesAndDirs:
                if i.endswith('.kicad_pcb') and not i.startswith('_autosave-'):
                    self.args.pcbfile = i
                    count += 1
            if not self.args.pcbfile:
                print("Error: Cannot find any .kicad_pcb file in project path " + self.args.ppath)
                exit()
            if count > 1:
                print("Error: Found multiple .kicad_pcb files in project path " + self.args.ppath + "\nPlease use -f flag")
                exit()

            if not os.path.isabs(self.args.pcbfile):
                self.args.pcbfile = self.args.ppath + os.path.sep + self.args.pcbfile

        print('ppath: '.ljust(20, ' ') + self.args.ppath)
        print('pcbfile: '.ljust(20, ' ') + self.args.pcbfile)

        if self.args.outputfile:
            fn = self.args.outputfile
            try:
                file = open(fn, mode='w', encoding='UTF8')
                file.close()
            except Exception as e:
                print('Error: cannot open output file for writing: ' + fn)
                exit()

        print()


    def readEnvironmentVariables(self):
        #######################################################################################################################
        #                                  READ ENVIRONMENT VARIABLES                                                         #
        #######################################################################################################################
        # read environment variables from kicad_common
        print('KiCad Environment Variables: ')
        self.kcc = KicadCommon(self.args.cpath, self.args.ppath)
        print(self.kcc)
        print()


    def readFootprintLibraryTables(self):
        #######################################################################################################################
        #                                  READ FP-LIB-TABLE(S)                                                              #
        #######################################################################################################################
        globFplt = LibTable(self.args.cpath + os.path.sep + "fp-lib-table")
        list = globFplt.getLibNames()

        if list:
            for w in list:
                wUri = LibGetUri(w)
                self.fpLibs[w.word] = self.kcc.expandPath(wUri.word)


        localFplt = None
        fn = os.path.join(self.args.ppath, 'fp-lib-table')
        if os.path.isfile(fn): # check for local fp-lib-table
            localFplt = LibTable(fn)

            list = localFplt.getLibNames()

            if list:
                for w in list:
                    if w.word in self.fpLibs.keys():
                        print("Warning: Overriding lib " + w.word + ' with entry from local fp-lib-table')
                    uri = LibGetUri(w)
                    self.fpLibs[w.word] = self.kcc.expandPath(uri.word)
                    # TODO 1: fails for this line in fp-lib-table:
                    #   (lib (name dsd-cc-eagle)(type KiCad)(uri "$(KIPRJMOD)/dsd-cc-eagle.pretty")(options "")(descr ""))
                    # vermutlich wegen doppelhochkomma!
        else:
            print("Info: No fp-lib-table in project path found")


        print('Libs in fp-lib-table(s): ')
        if list:
            sortedKeys = sorted(self.fpLibs.keys())

            for lib in sortedKeys:
                print(lib.ljust(30, ' ') + ' ' + self.fpLibs[lib])
        print()


    def readPcbFile(self):
        #######################################################################################################################
        #                                  READ PCB FILE   and   EXTRACT ITS FOOTPRINTS                                      #
        #######################################################################################################################

        print('Loading PCB file...')
        self.pcb = Layout(self.args.pcbfile)
        # pcb.mod.printTree()
        print()


        print('Footprints on PCB:')
        l = self.pcb.getFootprints()
        if l:
            for w in l:
                print(w.word)
                self.pcbFootprints.append(Footprint(w))
        print()

        # set footprintLibPath for all footprints on PCB:
        for fp in self.pcbFootprints:
            fp.footprintLibPath = self.fpLibs[fp.libName]



    def loadNeededFootprintFiles(self):
        #######################################################################################################################
        #                                  LOAD  FOOTPRINTS that are USED IN PCB FILE                                        #
        #######################################################################################################################
        print('Loading needed footprint files ...')
        for fp in sorted(self.pcbFootprints):
            id = fp.getFpId()
            if id not in self.usedFpSExpr.keys():
                fn = fp.footprintLibPath + os.path.sep + fp.libFP + '.kicad_mod'
                if os.path.isfile(fn):
                    self.usedFpSExpr[id] = SExpressionModifier(fn)
                    print(id.ljust(30, ' ') + '\t\t' + fn)
                else:
                    print("Warning: Cannot open footprint for " + fp.getFpId() + ': ' + fn +
                          "  These footprints will not be touched in the PCB file.")
        print('ok\n')


    def modifyPcbData(self):
        #######################################################################################################################
        #                                  MODIFY DATA in PCB FILE's S-EXPRESSIONS                                           #
        #######################################################################################################################
        print('Updating data in PCB file...')
        for fp in self.pcbFootprints:
            id = fp.getFpId()
            if id in self.usedFpSExpr.keys():
                result = findWord(self.usedFpSExpr[id]._tree, 'model', 0, True)

                if result:
                    if len(result) > 1:
                        print('Error: multiple models defined in ' + self.usedFpSExpr[id].fileName)
                    model3d = result[0]

                    # test, if new model file can be found on the system:
                    fn = model3d.getValue().word
                    if not os.path.isfile(self.kcc.expandPath(fn)):
                        print('Warning: cannot find new 3d model file: ' + fn)
                        print('         please check environment variables in ' + self.kcc.fileName)
                        print('         or the used footprint: ' + self.usedFpSExpr[id].fileName)
                        print('         or the used 3d models library.')

                        self.pcb.update3dModel(model3d, fp.pcbFP)
                else:
                    print("Trace: skip footprint " + self.usedFpSExpr[id].fileName  +
                          "  It has no model entry, which could be updated.")
            else:
                print("Info: Cannot update model for " + id) # this happens e.g. for eagle-libs

        print('ok\n')




    def writePcbFile(self):
        fn = self.pcb.fileName
        if self.args.outputfile:
            fn = self.args.outputfile

        print('Writing to PCB file: ' + fn)
        self.pcb.sexp.writeTree(fn)
        print('ok\n')




app = App()
app.run()
