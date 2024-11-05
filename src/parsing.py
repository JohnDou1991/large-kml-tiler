import src.common.config as config
import src.common.input as input
import src.tiling as tiling
import src.misc as misc
import src.geometry as geometry
import src.utils.progress as progress
import src.kml as kml

import xml.etree.ElementTree
import os

def ReadAndParseInputFile(file:str):
    print("Read and parse: " + file.split('/')[-1])
    return xml.etree.ElementTree.parse(file)

def ExtractCoordinatesFromText(text):
    result = []
    for text in text.split('\n'):
        if len(text) != 0:
            splitted_coordinate = text.split(',')
            lat=float(splitted_coordinate[0])
            lon=float(splitted_coordinate[1])
            result.append(geometry.Coordinate(lat,lon))
    return result

def ExtractAllCoordinates(parsed_kml):
    print("Extract all coordinates...", end=' ')
    ns = {'ns':'http://www.opengis.net/kml/2.2'}
    result = []
    for coordinates in parsed_kml.findall(".//*ns:coordinates", ns):
        raw_text = coordinates.text
        if not raw_text.count('\n') > 4: # skip bboxes
            coords = ExtractCoordinatesFromText(raw_text)
            result.append(coords[0])
            result.append(coords[1])
    print(str(len(result)))
    return result

def ExtractAllLines(parsed_kml):
    ns = {'ns':'http://www.opengis.net/kml/2.2'}
    result = []
    prog = progress.Progress('Extract all lines')
    placemarks = parsed_kml.findall(".//*ns:Placemark", ns)

    for index, placemark in enumerate(placemarks):
        prog.update(int(index / len(placemarks) * 100))

        linestring = placemark.find(".//ns:LineString", ns)
        coordinates = linestring.find(".//ns:coordinates", ns)

        styleUrl = placemark.find(".//ns:styleUrl", ns)

        raw_text = coordinates.text
        if not raw_text.count('\n') > 4: # skip bboxes
            coords = ExtractCoordinatesFromText(raw_text)
            result.append(geometry.Line(coords[0], coords[1]))
        
        timestamp = placemark.find(".//ns:TimeStamp", ns)
        when = timestamp.find(".//ns:when", ns)
        if not when is None:
            result[-1].when = when.text


        description = placemark.find(".//ns:description", ns)
        if not description is None:
            result[-1].description = description.text
        name = placemark.find(".//ns:name", ns)
        if not name is None:
            result[-1].name = name.text
        if not styleUrl is None:
            result[-1].style = styleUrl.text

    prog.finish(' (' + str(len(result)) + ')')
    return result

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
            tree = kml.CreateTree(id, lines, generator.getBoundingBox(id), lvl)
            kml.WriteDownKmlTree(tree, output_filename)
        processed_lines += len(distributed_lines[lvl])
        prog.update(int(processed_lines / total_line_count * 100))
    prog.finish('')