import src.common.config as config
import src.cli as cli
import src.utils.progress as progress

import xml.etree.ElementTree
import os
import shutil

def CreateDocFile(file_count:int):
    prog = progress.Progress('Compute doc.kml')
    root = xml.etree.ElementTree.parse("resources/doc.kml")
    ns = {'ns':'http://www.opengis.net/kml/2.2'}
    doc = root.find(".//ns:Document", ns)
    level = 'Level' + str(config.levels[-1])
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

def CreateArchive():
    prog = progress.Progress('Create result archive')
    shutil.make_archive(cli.output.folder + '/' + cli.output.folder, 'zip', config.temp_folder)
    prog.update(33)
    os.rename(cli.output.folder + '/' + cli.output.folder + '.zip', cli.output.folder + '/' + cli.output.file + '.kmz')
    prog.update(66)
    shutil.rmtree(config.temp_folder)
    prog.finish()