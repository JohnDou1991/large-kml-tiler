import src.common.config as config
import src.common.stats as stats

import xml.etree.ElementTree

def Region(placemark, bbox, tile_level):
    region = xml.etree.ElementTree.SubElement(placemark, "Region")
    altBox = xml.etree.ElementTree.SubElement(region, "LatLonAltBox")
    xml.etree.ElementTree.SubElement(altBox, "north").text = str(bbox.ne.longitude)
    xml.etree.ElementTree.SubElement(altBox, "south").text = str(bbox.sw.longitude)
    xml.etree.ElementTree.SubElement(altBox, "east").text = str(bbox.sw.latitude)
    xml.etree.ElementTree.SubElement(altBox, "west").text = str(bbox.ne.latitude)

    lod = xml.etree.ElementTree.SubElement(region, "Lod")
    if tile_level != config.levels[-1]:
        xml.etree.ElementTree.SubElement(lod, "minLodPixels").text = '256'
    # if tile_level != 11:
    #     xml.etree.ElementTree.SubElement(lod, "maxLodPixels").text = '1024'

def Lines(folder, lines):
    lines_folder = xml.etree.ElementTree.SubElement(folder, "Folder")
    xml.etree.ElementTree.SubElement(lines_folder, "name").text = "Lines"

    for line in lines:
        placemark = xml.etree.ElementTree.SubElement(lines_folder, "Placemark")
        xml.etree.ElementTree.SubElement(placemark, "styleUrl").text = str(line.style)
        # timestamp = xml.etree.ElementTree.SubElement(placemark, "TimeStamp")
        # xml.etree.ElementTree.SubElement(timestamp, "when").text = line.when
        linestring = xml.etree.ElementTree.SubElement(placemark, "LineString")
        xml.etree.ElementTree.SubElement(linestring, "coordinates").text = (
            str(line.coordinate_from.latitude) + ',' + str(line.coordinate_from.longitude) + '\n' +
            str(line.coordinate_to.latitude) + ',' + str(line.coordinate_to.longitude)
        )
        xml.etree.ElementTree.SubElement(placemark, "description").text = line.description
        xml.etree.ElementTree.SubElement(placemark, "name").text = line.name

def BBox(folder, bbox):
    placemark = xml.etree.ElementTree.SubElement(folder, "Placemark")
    xml.etree.ElementTree.SubElement(placemark, "name").text = "BoundingBox"
    xml.etree.ElementTree.SubElement(placemark, "styleUrl").text = "#m_ylw-pushpin"

    linestring = xml.etree.ElementTree.SubElement(placemark, "LineString")
    xml.etree.ElementTree.SubElement(linestring, "tessellate").text = "1"

    xml.etree.ElementTree.SubElement(linestring, "coordinates").text = (
        str(bbox.sw.latitude) + ',' + str(bbox.sw.longitude) + '\n' +
        str(bbox.ne.latitude) + ',' + str(bbox.sw.longitude) + '\n' +
        str(bbox.ne.latitude) + ',' + str(bbox.ne.longitude) + '\n' +
        str(bbox.sw.latitude) + ',' + str(bbox.ne.longitude) + '\n' +
        str(bbox.sw.latitude) + ',' + str(bbox.sw.longitude) + '\n'
    )

# probably it is more efficient to dump each tile into separate file
# in order to network link them afterwards
# this will enable nested regions, which might solve lags on large scales
def Tile(folder, bbox, tile_id, lines, tile_level):
    stats.dump_count[tile_level] = stats.dump_count[tile_level] + len(lines)
    Region(folder, bbox, tile_level)
    Lines(folder, lines)
    # BBox(folder, bbox)
    # print(str(tile_level) + '/' + str(tile[0].x) + ':' + str(tile[0].y))