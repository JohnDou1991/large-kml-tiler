import src.dump as dump

import xml.etree.ElementTree
import os.path

def AppendData(lhs:xml.etree.ElementTree, rhs:xml.etree.ElementTree):
    ns = {'ns':'http://www.opengis.net/kml/2.2'}
    doc = lhs.find(".//Document")
    folder = doc.find(".//Folder")
    if folder.find('name').text == 'Lines':
        for line in rhs.findall(".//Placemark", ns):
            folder.append(line)

    return lhs

def WriteDownKmlTree(root:xml.etree.ElementTree, output_file):

    if os.path.exists(output_file):
        r = xml.etree.ElementTree.parse(output_file)
        tree = AppendData(r, root)
    else:
        tree = xml.etree.ElementTree.ElementTree(root)
    tree.write(output_file)

def CreateTree(tile_id, lines, bbox, tile_level):

    root = xml.etree.ElementTree.Element("kml")
    doc = xml.etree.ElementTree.SubElement(root, "Document")
    xml.etree.ElementTree.SubElement(doc, "name").text = "L" + str(tile_level) + ':' + str(tile_id.x) + ':' + str(tile_id.y)

    styles = xml.etree.ElementTree.parse("resources/styles.xml")
    for element in styles.getroot().findall(".//"):
        doc.append(element)

    dump.Tile(doc, bbox, tile_id, lines, tile_level)

    return root