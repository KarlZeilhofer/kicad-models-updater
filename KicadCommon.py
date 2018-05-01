# This file is part of kicad-models-updater
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




# file parser for kicad_common,
# with is in ~/config/kicad
#
# Limitations
# expandPath supports only one replacement at a time

import os
import re


class KicadCommon:
    def __init__(self, path: str, projectPath: str):
        self.envVars = {}  # environment variables, str variable -> str path
        self.fileName = path + os.path.sep + 'kicad_common'

        self.envVars['KIPRJMOD'] = projectPath

        try:
            file = open(self.fileName, mode='r', encoding='UTF8')

            nr = 0
            inEnvVarGroup = False
            for line in file:
                if not line.startswith('#'):
                    if inEnvVarGroup:
                        result = re.search("\s*([A-Za-z_]+[A-Za-z0-9_]*)\s*=\s*(.+)", line)

                        if result:
                            key = result.group(1)
                            value = result.group(2)
                            if value.startswith('\"'):
                                if value.endswith('\"'):
                                    value = value[1:-1]
                                else:
                                    print("Error: missing 2nd \" in " + self.fileName)
                            self.envVars[key] = value

                    elif '[EnvironmentVariables]' in line:
                        inEnvVarGroup = True

        except Exception as e:
            print(e)

    # replace every ocurrance of a KiCad Environment Variable in a given string
    # returns the expanded string
    def expandPath(self, filePath):
        results = re.search('(.*)\${(.+?)}(.*)', filePath)

        if results:
            if results.group(2) in self.envVars.keys():
                return results.group(1) + self.envVars[results.group(2)] + results.group(3)

        return filePath

    def __str__(self):
        sortedKeys = sorted(self.envVars.keys())
        s = ''
        for k in sortedKeys:
            s += k.ljust(30, ' ')
            s += ' '
            s += self.envVars[k]
            s += '\n'

        return s