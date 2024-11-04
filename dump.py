import xml, os, config, progress

def region(placemark, bbox, tile_level):
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

def lines(folder, lines):
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

def bbox(folder, bbox):
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

def createDocFile(file_count:int):
    prog = progress.Progress('Compute doc.kml')
    root = xml.etree.ElementTree.parse("resources/doc.kml")
    ns = {'ns':'http://www.opengis.net/kml/2.2'}
    doc = root.find(".//ns:Document", ns)
    level = 'Level1'
    for dir, subdirs, files in os.walk(config.temp_folder + '/' + level):
        for file in files:
            nlink = xml.etree.ElementTree.SubElement(doc, "NetworkLink")
            name = os.path.join(dir, file).removeprefix(config.temp_folder + '/')
            xml.etree.ElementTree.SubElement(nlink, "name").text = 'L' + name.removeprefix('Level').removesuffix('.kml').replace('/',':')
            link = xml.etree.ElementTree.SubElement(nlink, "Link")
            xml.etree.ElementTree.SubElement(link, "href").text = name
        prog.update(int(len(files) / file_count * 100))

    root.write(config.temp_folder + '/doc.kml')
    prog.finish()