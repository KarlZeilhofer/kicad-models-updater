Changelog kicad-models-updater
==============================
Karl Zeilhofer, www.team14.at
------------------------------


# Development
* CLI (command line interface) to set
  * config path for KiCad
  * set project path
  * set .kicad_pcb file
* SExpressionModifier
  * parses a S-Expression file
  * keeps structure of file
  * each word can be modified in place
* refactored project name to 'kicad-models-updater'

## TODOs
* write file
* search and parse .kicad_mod files with footprints and 3D file path
* update .kicad_pcb file with found 3D file paths
* Use correct default config path on Windows/Mac
* test on Windows
* test with spaces in
  * 3D file path
  * config path
  * project path
