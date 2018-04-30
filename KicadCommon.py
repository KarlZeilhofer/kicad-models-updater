

# file parser for kicad_common,
# with is in ~/config/kicad
#
# Limitations
# expandPath supports only one replacement




import os
import re


class KicadCommon:
    envVars = {}  # environment variables

    def __init__(self, path):
        fileName = path + os.path.sep + 'kicad_common'

        try:
            file = open(fileName, mode='r', encoding='UTF8')

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
                                    print("Error: missing 2nd \" in " + fileName)
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
        s = ''
        for k in self.envVars.keys():
            s += k
            s += '='
            s += self.envVars[k]
            s += '\n'

        return s