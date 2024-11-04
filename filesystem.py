import xml.etree.ElementTree;
import geometry
import progress
import input

def ReadAndParseInputFile(file:str):
    print("Read and parse: " + file.removeprefix(input.root + '/' + input.folder + '/'))
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