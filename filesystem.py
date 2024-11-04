import xml.etree.ElementTree;
import geometry

def ReadAndParseInputFile(file):
    print("Read and parse input file: " + file)
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
    print("Extract all lines...", end=' ')
    ns = {'ns':'http://www.opengis.net/kml/2.2'}
    result = []

    for placemark in parsed_kml.findall(".//*ns:Placemark", ns):
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

    print(str(len(result)))
    return result