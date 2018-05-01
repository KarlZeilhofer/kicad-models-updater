Changelog kicad-models-updater
==============================
Karl Zeilhofer, www.team14.at
------------------------------


# 18.0.0, first release
* add option `--version`
* add installation instructions
* updated help

# Initial Development
* CLI (command line interface) to set
  * config path for KiCad
  * set project path
  * set .kicad_pcb file
* SExpressionModifier
  * parses a S-Expression file
  * keeps structure of file
  * each word can be modified in place
* refactored project name to 'kicad-models-updater'
* write file
* search and parse .kicad_mod files with footprints and 3D file path
* update .kicad_pcb file with found 3D file paths
* add copyright and
* ignore `_autosave-` files
* add output file option -o --output
* Use (hopefully) correct default config path on Windows/Mac
* add project path to environment variables KIPJMOD
* sort some printed lists
* moved Footprint class into module Layout
* reordered steps, to get faster errors
* report missing file of 3D model
* fixed use of local fp-lib-table
* refactored main script into a class App
* add output formatting with ljust()
* major bugfix: fixed parser for escaped double quote!
* Error for PCB footprints with multiple models
* warning for PCB footrpints without any footprint id (e.g. @HOLE0)

## TODOs
* use DebugTrace module (see kicad-partslist-editor)
* test on Windows and Mac
* test with spaces and double quotes for
  * 3D file path
  * config path
  * project path
