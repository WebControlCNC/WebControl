gcode clean command line interface utility is called from a folder next to the Webcontrol folder.

You must install the correct gcodeclean files for your operating system in a folder alongside Webcontrol.
Once it is installed, then webcontrol gcode clean menus will function.

CLI 0.9.4+
Copyright (C) 2022 md8n (forums.maslowcnc.com)
USAGE:
Clean GCode file:
  GCodeClean --filename facade.nc

  --filename        Required. Full path to the input filename.

  --tokenDefs       (Default: tokenDefinitions.json) Full path to the
                    tokenDefinitions.json file.

  --annotate        Annotate the GCode with inline comments.

  --minimise        (Default: soft) Select preferred minimisation strategy,
                    'soft' - (default) FZ only, 'medium' - All codes excluding
                    IJK (but leave spaces in place), 'hard' - All codes
                    excluding IJK and remove spaces, or list of codes e.g. FGXYZ

  --tolerance       Enter a clipping tolerance for the various deduplication
                    operations
                    Minimum: 0.00005 (default).  Maximum: 0.5

  --arcTolerance    Enter a tolerance for the 'point-to-point' length of arcs
                    (G2, G3) below which they will be converted to lines (G1)
                    Minimum: 0.00005 (default).  Maximum: 0.5

  --zClamp          Restrict z-axis positive values to the supplied value
                    Unit dependent selected by the G20 or G21.  
                    Minimum (mm): 0.5 (default).  Maximum (mm) 10.
                    Minimum (in): 0.02 (default).  Maximum (in) 0.5.

  --help            Display this help screen.

  --version         Display version information.

Exit code= 0
