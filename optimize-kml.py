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
    step = 2 ** (config.levels[0] - config.levels[1]) # no good
    tile_id.x = tile.x * step
    tile_id.y = tile.y * step

    # this is wrong
    for i in range(step):
        for j in range(step):
            id = tiling.TileId()
            id.x = tile_id.x + i
            id.y = tile_id.y + j

            if id in tiling.unique_tiles[tile_level]:
                tile_id_str = str(id.x) + ':' + str(id.y)
                output_filename = level_dir + '/' + tile_id_str + '.kml'
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
    processed_lines = 0
    total_line_count = len(parsed_lines)

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
        processed_lines += len(distributed_lines[lvl])
        prog.update(int(processed_lines / total_line_count * 100))
    prog.finish('')

link_tree = {
    1:
        {
        }
}

def SetUplink(level:int, uplink: tiling.TileId, level2:int, id:tiling.TileId):
    global link_count

    if level < config.levels[-1]:
        return

    if uplink in tiling.unique_tiles[level]:
        if not level in link_tree:
            link_tree[level] = {uplink.ToString():[tuple([level2,id])]}
        elif not uplink.ToString() in link_tree[level]:
            link_tree[level][uplink.ToString()] = [tuple([level2,id])]
        else:
            link_tree[level][uplink.ToString()].append(tuple([level2,id]))
    else:
        up_tile_id = tiling.TileId()
        up_tile_id.x = int(uplink.x / 4)
        up_tile_id.y = int(uplink.y / 4)
        SetUplink(level-2, up_tile_id, level2, id)

def LinkTiles(total_file_count:int):
    prog = progress.Progress("Link tiles")
    processed_count = 0
    for level in reversed(sorted(config.levels)):
        for tile_id in tiling.unique_tiles[level]:
            up_tile_id = tiling.TileId()
            up_tile_id.x = int(tile_id.x / 4)
            up_tile_id.y = int(tile_id.y / 4)
            SetUplink(level-2, up_tile_id, level, tile_id)

    for level in reversed(sorted(config.levels)):
        if level == config.levels[0]:
            continue

        dir = config.temp_folder + '/' + 'Level' + str(level)
        for index, file in enumerate(os.listdir(dir)):
            root = xml.etree.ElementTree.parse(os.path.join(dir, file))
            doc = root.find(".//Document")
            if not doc is None and not doc.find("Region") is None:
                tile_str = file.removesuffix('.kml')
                if tile_str in link_tree[level].keys():
                    for lvl, id in link_tree[level][tile_str]:

                        level_folder = 'Level' + str(lvl)
                        level_dir = config.temp_folder + '/' + level_folder
                        tile_id_str = str(id.x) + ':' + str(id.y)
                        output_filename = level_dir + '/' + tile_id_str + '.kml'
                        kml = xml.etree.ElementTree.parse(output_filename)
                        region = kml.find(".//Region")
                        nlink = xml.etree.ElementTree.SubElement(doc, "NetworkLink")
                        nlink.append(region)
                        link = xml.etree.ElementTree.SubElement(nlink, "Link")
                        xml.etree.ElementTree.SubElement(nlink, "name").text = 'L' + str(lvl) + ':' + tile_id_str
                        xml.etree.ElementTree.SubElement(link, "href").text = output_filename.replace(config.temp_folder + '/', '../')
                        xml.etree.ElementTree.SubElement(link, "viewRefreshMode").text = 'onRegion'

                root.write(os.path.join(dir, file))
                prog.update(int((processed_count + index) / total_file_count * 100))
        processed_count = processed_count + index
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
total_files_count=0
for tiles in tiling.unique_tiles.values():
    total_files_count += len(tiles)
LinkTiles(total_files_count)
dump.createDocFile(total_files_count)
CreateResultKmz()

end = time.time()
print("Elapsed time: " + str(end - start) + " seconds")

# stats.dump()