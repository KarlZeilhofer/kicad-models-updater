kicad-models-updater
====================
A Python Script to Update the 3D Models of a .kicad_pcb File
------------------------------------------------------------

You would like to use this script, if you have modified the 3D models
in your footprint libraries.

It takes a `.kicad_pcb` file, laods the used footprints from the
libraries and modifies the entries for a 3D model in the PCB file
without modifying any other fields. A diff will show only
the intended modifications (great for git).

## Usage
run `kicad-models-updater` in your KiCad project directory, and the
rest should be done by the script.

If you have multiple config paths on your system (e.g. KiCad 4/5 in
parallel), you have to specify
one of them with `-c CONFIGPATH`.

## Help
```
$ python3 kicad-models-updater.py -h
usage: kicad-models-updater [-h] [-c CPATH] [-p PPATH] [-f PCBFILE]

Gets paths for 3D models from the used footrints and updates it in the
.kicad_pcb file without changing any other properties in the layout.

optional arguments:
  -h, --help            show this help message and exit
  -c CPATH, --configpath CPATH
                        system wide config path, where kicad_comman and fp-
                        lib-table can be found. Default is
                        /home/karl/.config/kicad
  -p PPATH, --projectpath PPATH
                        path to kicad project, where .kicad_pcb and optional
                        fp-lib-table can be found. Default is the current
                        working directory
  -f PCBFILE, --pcbfile PCBFILE
                        .kicad_pcb file to be modified. Default is the
                        .kicad_pcb in the project path.

GitHub: https://github.com/KarlZeilhofer/kicad-models-updater
```

## Details
The footprint libraries are discoverd like they are discovered by KiCad
itself using `kicad_common`, global `fp-lib-table` and projcet's
`fp-lib-table`.
This leads to a very smooth user experience and best possible
integrity of the modifications.

Various warnings are reported, if something isn't as expected:
* missing kicad_common
* missing fp-lib-table
* missing footprint library
* missing 3D model file
* ...

## Status
* tested on linux with python 3.5.2

## Limitations
* only for KiCad 4 and newer with fp-lib-table and .pretty libs
* path substitutions are applied onyl once (`KicadCommon.py`)


## License
GPL V3
(c) Karl Zeilhofer, www.team14.at