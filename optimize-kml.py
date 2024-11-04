import xml.etree.ElementTree;

import dump
import filesystem

import misc
import os, shutil
import stats
import tiling
import time

# input = 'full-2'
# input = "full"
# input = 'medium'
# input = 'light'
# input = 'soft'
input = 'custom'
# input = 'custom-light'

input_folder = 'input'
output_folder = "output"
temp_folder = "temp"
output_file = input + "-tiled"
zoom_lvl=13

established_links = {}

def AddNetworkLinks(folder, tile, tile_level):
    
    if tile_level > 13:
        return

    level_folder = 'Level' + str(tile_level)
    level_dir = temp_folder + '/' + level_folder

    tile_id   = tiling.TileId()
    tile_id.x = tile.x * 4
    tile_id.y = tile.y * 4

    for i in range(4):
        for j in range(4):
            tile_id_str = str(tile_id.x+i) + ':' + str(tile_id.y+j)
            output_filename = level_dir + '/' + tile_id_str + '.kml'

            if os.path.exists(output_filename):
                kml = xml.etree.ElementTree.parse(output_filename)
                region = kml.find(".//Region")
                nlink = xml.etree.ElementTree.SubElement(folder, "NetworkLink")
                nlink.append(region)
                link = xml.etree.ElementTree.SubElement(nlink, "Link")
                xml.etree.ElementTree.SubElement(nlink, "name").text = 'L' + str(tile_level) + ':' + tile_id_str
                xml.etree.ElementTree.SubElement(link, "href").text = output_filename.replace('temp/', '../')
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

def AppendData(lhs:xml.etree.ElementTree, rhs:xml.etree.ElementTree):
    ns = {'ns':'http://www.opengis.net/kml/2.2'}
    doc = lhs.find(".//Document")
    folder = doc.find(".//Folder")
    if folder.find('name').text == 'Lines':
        for line in rhs.findall(".//Placemark", ns):
            folder.append(line)

        # for child in folder:
        #     print(child.tag, child.attrib, child.text)
        # print("Append data...")
        # for line in rhs.findall(".//Placemark", ns):
        #     folder.append(line)
    # print('\n')

    return lhs

def CreateKmlTree(tile_id, lines, bbox, tile_level):

    root = xml.etree.ElementTree.Element("kml")
    doc = xml.etree.ElementTree.SubElement(root, "Document")
    xml.etree.ElementTree.SubElement(doc, "name").text = "L" + str(tile_level) + ':' + str(tile_id.x) + ':' + str(tile_id.y)

    styles = xml.etree.ElementTree.parse("resources/styles.xml")
    for element in styles.getroot().findall(".//"):
        doc.append(element)

    DumpTile(doc, bbox, tile_id, lines, tile_level)

    return root

def WriteDownKmlTree(root:xml.etree.ElementTree, output_file):

    if os.path.exists(output_file):
        r = xml.etree.ElementTree.parse(output_file)
        tree = AppendData(r, root)
    else:
        tree = xml.etree.ElementTree.ElementTree(root)
    tree.write(output_file)


levels = [13,11,9,7,5,3,1]

start = time.time()

if not os.path.isdir(temp_folder):
    os.mkdir(temp_folder)

for indx, file in enumerate(os.listdir(input_folder + '/' + input)):
    parsed_kml = filesystem.ReadAndParseInputFile(input_folder + '/' + input + '/' + file)
    parsed_lines = filesystem.ExtractAllLines(parsed_kml)
    distributed_lines = misc.distribute(parsed_lines)
    for lvl in levels:
        generator = tiling.TileIdGenerator(lvl)
        level_folder = 'Level' + str(lvl)
        level_dir = temp_folder + '/' + level_folder
        if not os.path.isdir(level_dir):
            os.mkdir(level_dir)
        tiles = tiling.DetermineAffectedTiles2(distributed_lines[lvl], lvl)
        for id,lines in tiles.items():
            output_filename = level_dir + '/' + str(id.x) + ':' + str(id.y) + '.kml'
            tree = CreateKmlTree(id, lines, generator.getBoundingBox(id), lvl)
            WriteDownKmlTree(tree, output_filename)

# def AddNetworkLinks(folder, tile, tile_level)

for dir, subdirs, files in os.walk('temp'):
    for file in files:
        root = xml.etree.ElementTree.parse(os.path.join(dir, file))
        doc = root.find(".//Document")
        if not doc is None and not doc.find("Region") is None:
            tile = file.removesuffix('.kml').split(':')
            id = tiling.TileId()
            id.x = int(tile[0])
            id.y = int(tile[1])
            AddNetworkLinks(doc, id, int(dir.removeprefix('temp/Level')) + 2)
            root.write(os.path.join(dir, file))

dump.createDocFile()

print("Create result KMZ...")
shutil.make_archive(output_folder + '/' + output_file, 'zip', temp_folder)
os.rename(output_folder + '/' + output_file + '.zip', output_folder + '/' + output_file + '.kmz')
shutil.rmtree(temp_folder)

end = time.time()
print("Elapsed time: " + str(end - start) + " seconds")
stats.dump()