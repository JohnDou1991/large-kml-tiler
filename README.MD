This is a super proprietary script, will not work with almost anything.

This script exists because working with large raw kmls is bloody suffering.
It is designed to boost search space kmls performance.

All optimizations are coming from here: https://developers.google.com/kml/documentation/regions#regionbasednl

This script does:
 - reads input kml files one by one and extracts all LineString objects
 - arranges lines into groups(tiles) that correspond to tile levels (based on geometry size)
 - for every tile coordinate(tile) separate kml file is being created
 - insert into these kmls special tag and bbox that serve as a hint for google earth tiling
 - it is posible that different kmls inerlieve at tile coordinates. Such LineStrings are being dumped into single tile kml file
 - after these steps we have folders that correspond to each tile level and kml files in them that represent tiled data
 - we iterate over every tile kml file and calculate tile coordinates that potentially present on next tile level below this tile, then check if corresponding tile kmls on next level exist and if so, then kml file is being modified with new entry that links this tile and tiles on next level. This is being done from top to down, means kml from higher level contains links to tiles on lower level. This helps Google Earth more efficiently manage tiled data
 - doc.kml file, that links to higher level kmls, serves as an entry point for kmz
 - make kmz file

In short this script breaks input raw data into efficient tiled structure and packs it into kmz.
kmz format helps to keep things in one piece and save up to 10x space.

Major todo's:
 - need to avoid re-read or post-edit of kml files
 - solid refactor is required
 - comfy cli interface is required

Minor todo's:
 - come up with better level of details algorithm, for better presentation on large scales and more fluent transition
 - better balance geometries among tile levels for uniform performance on all scales
 - fix tile bounding box calculation
 - probably kmz layout can be improved for better appearance in GE's file explorer