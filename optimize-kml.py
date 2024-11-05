import src.common.config as config
import src.common.stats as stats

import src.cli as cli
import src.kmz as kmz
import src.link_tree as link_tree
import src.parsing as parsing

import os
import time

cli.parse_argvs()

start = time.time()

if not os.path.isdir(config.temp_folder):
    os.mkdir(config.temp_folder)

print('------Process Input------')
path = os.path.abspath(os.path.expanduser(cli.input.folder))
for indx, file in enumerate(os.listdir(path)):
    parsed_kml = parsing.ReadAndParseInputFile(path + '/' + file)
    parsed_lines = parsing.ExtractAllLines(parsed_kml)
    parsing.DistributeLines(parsed_lines)

print('------Prepare Output------')
total_files_count=0
for tiles in stats.unique_tiles.values():
    total_files_count += len(tiles)
link_tree.LinkTiles(total_files_count)
kmz.CreateDocFile(total_files_count)
kmz.CreateArchive()

end = time.time()
print('------DONE------')
print("Elapsed time: " + str(end - start) + " seconds")

# stats.dump()