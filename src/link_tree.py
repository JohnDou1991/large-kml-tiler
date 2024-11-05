import src.common.config as config
import src.utils.progress as progress
import src.tiling as tiling

import xml.etree.ElementTree
import os

link_tree = {
    1:
        {
        }
}

def SetUplink(level:int, uplink: tiling.TileId, level2:int, id:tiling.TileId):
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

def SetUplinks(total_file_count:int):
    prog = progress.Progress("Set uplinks")
    processed=0
    for level in reversed(sorted(config.levels)):
        for index, tile_id in enumerate(tiling.unique_tiles[level]):
            up_tile_id = tiling.TileId()
            up_tile_id.x = int(tile_id.x / 4)
            up_tile_id.y = int(tile_id.y / 4)
            SetUplink(level-2, up_tile_id, level, tile_id)
            prog.update(int((processed+index) / total_file_count * 100))
        processed += len(tiling.unique_tiles[level])
    prog.finish()

def AddNetworkLink(lvl:int, id:tiling.TileId, doc:xml.etree.ElementTree):
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

def AddNetworkLinks(total_file_count:int):
    prog = progress.Progress("Link tiles")
    processed_count = 0
    for level in reversed(sorted(config.levels)):
        if level == config.levels[0]:
            processed_count += len(tiling.unique_tiles[level])
            continue

        dir = config.temp_folder + '/' + 'Level' + str(level)
        for index, file in enumerate(os.listdir(dir)):
            root = xml.etree.ElementTree.parse(os.path.join(dir, file))
            doc = root.find(".//Document")
            if not doc is None and not doc.find("Region") is None:
                tile_str = file.removesuffix('.kml')
                if tile_str in link_tree[level].keys():
                    for lvl, id in link_tree[level][tile_str]:
                        AddNetworkLink(lvl, id, doc)

                root.write(os.path.join(dir, file))
                prog.update(int((processed_count + index) / total_file_count * 100))
        processed_count = processed_count + index
    prog.finish()

def LinkTiles(total_file_count:int):
    SetUplinks(total_file_count)
    AddNetworkLinks(total_file_count)