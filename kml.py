import os.path
import xml.etree.ElementTree;

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

def WriteDownKmlTree(root:xml.etree.ElementTree, output_file):

    if os.path.exists(output_file):
        r = xml.etree.ElementTree.parse(output_file)
        tree = AppendData(r, root)
    else:
        tree = xml.etree.ElementTree.ElementTree(root)
    tree.write(output_file)