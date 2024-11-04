import xml.etree.ElementTree;

import cli, config, progress
import dump
import filesystem

import kml
import misc
import os, shutil
import stats
import tiling
import time, sys

def AddNetworkLinks(folder, tile, tile_level):
    
    if tile_level > config.levels[0]:
        return

    level_folder = 'Level' + str(tile_level)
    level_dir = config.temp_folder + '/' + level_folder

    tile_id   = tiling.TileId()
    step = 2 ** (config.levels[0] - config.levels[1])
    tile_id.x = tile.x * step
    tile_id.y = tile.y * step

    for i in range(step):
        for j in range(step):
            tile_id_str = str(tile_id.x+i) + ':' + str(tile_id.y+j)
            output_filename = level_dir + '/' + tile_id_str + '.kml'

            if os.path.exists(output_filename):
                kml = xml.etree.ElementTree.parse(output_filename)
                region = kml.find(".//Region")
                nlink = xml.etree.ElementTree.SubElement(folder, "NetworkLink")
                nlink.append(region)
                link = xml.etree.ElementTree.SubElement(nlink, "Link")
                xml.etree.ElementTree.SubElement(nlink, "name").text = 'L' + str(tile_level) + ':' + tile_id_str
                xml.etree.ElementTree.SubElement(link, "href").text = output_filename.replace(config.temp_folder + '/', '../')
                xml.etree.ElementTree.SubElement(link, "viewRefreshMode").text = 'onRegion'

# probably it is more efficient to dump each tile into seprate file
# in order to network link them afterwards
# this will enable nested regions, which might solve lags on large scales
def DumpTile(folder, bbox, tile_id, lines, tile_level):
    stats.dump_count[tile_level] = stats.dump_count[tile_level] + len(lines)
    dump.region(folder, bbox, tile_level)
    dump.lines(folder, lines)
    # dump.bbox(folder, bbox)
    # print(str(tile_level) + '/' + str(tile[0].x) + ':' + str(tile[0].y))
    # AddNetworkLinks(folder, tile_id, tile_level + 2)

def CreateKmlTree(tile_id, lines, bbox, tile_level):

    root = xml.etree.ElementTree.Element("kml")
    doc = xml.etree.ElementTree.SubElement(root, "Document")
    xml.etree.ElementTree.SubElement(doc, "name").text = "L" + str(tile_level) + ':' + str(tile_id.x) + ':' + str(tile_id.y)

    styles = xml.etree.ElementTree.parse("resources/styles.xml")
    for element in styles.getroot().findall(".//"):
        doc.append(element)

    DumpTile(doc, bbox, tile_id, lines, tile_level)

    return root

def DistributeLines(parsed_lines) -> int:
    distributed_lines = misc.distribute(parsed_lines)
    prog = progress.Progress('Distribute lines by tiles')
    for lvl in config.levels:
        generator = tiling.TileIdGenerator(lvl)
        level_folder = 'Level' + str(lvl)
        level_dir = config.temp_folder + '/' + level_folder
        if not os.path.isdir(level_dir):
            os.mkdir(level_dir)
        tiles = tiling.DetermineAffectedTiles2(distributed_lines[lvl], lvl)
        for id,lines in tiles.items():
            output_filename = level_dir + '/' + str(id.x) + ':' + str(id.y) + '.kml'
            tree = CreateKmlTree(id, lines, generator.getBoundingBox(id), lvl)
            kml.WriteDownKmlTree(tree, output_filename)
        prog.update(int(len(distributed_lines[lvl]) / len(parsed_lines) * 100))
    prog.finish('')

def LinkTiles(total_file_count:int):
    prog = progress.Progress("Link tiles")
    processed_count = 0
    for dir, subdirs, files in os.walk(config.temp_folder):
        for index, file in enumerate(files):
            root = xml.etree.ElementTree.parse(os.path.join(dir, file))
            doc = root.find(".//Document")
            if not doc is None and not doc.find("Region") is None:
                tile = file.removesuffix('.kml').split(':')
                id = tiling.TileId()
                id.x = int(tile[0])
                id.y = int(tile[1])
                AddNetworkLinks(doc, id, int(dir.removeprefix(config.temp_folder + '/Level')) + 2)
                root.write(os.path.join(dir, file))
                prog.update(int((processed_count + index) / total_file_count * 100))
        processed_count += len(files)
    prog.finish()

def CreateResultKmz():
    prog = progress.Progress('Create result KMZ archive')
    shutil.make_archive(cli.output.folder + '/' + cli.output.folder, 'zip', config.temp_folder)
    prog.update(33)
    os.rename(cli.output.folder + '/' + cli.output.folder + '.zip', cli.output.folder + '/' + cli.output.file + '.kmz')
    prog.update(66)
    shutil.rmtree(config.temp_folder)
    prog.finish()

cli.parse_argvs()

start = time.time()

if not os.path.isdir(config.temp_folder):
    os.mkdir(config.temp_folder)

print('------Process Input------')
for indx, file in enumerate(os.listdir(cli.input.root + '/' + cli.input.folder)):
    parsed_kml = filesystem.ReadAndParseInputFile(cli.input.root + '/' + cli.input.folder + '/' + file)
    parsed_lines = filesystem.ExtractAllLines(parsed_kml)
    DistributeLines(parsed_lines)

print('------Prepare Output------')
total_files_count = len(tiling.unique_tiles)
LinkTiles(total_files_count)
dump.createDocFile(total_files_count)
CreateResultKmz()

end = time.time()
print("Elapsed time: " + str(end - start) + " seconds")

# stats.dump()