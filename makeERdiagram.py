import sys
import argparse
import xml.etree.ElementTree as ETree
import os
import metadata as md

def createParser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--srcPath')
    parser.add_argument('-o', '--output')

    return parser

def validateParams(params):
    if params.output is None:
        params.output = "output.puml"    

def connectIcons():
    return """\n!define v8_PUML https://raw.githubusercontent.com/astrizhachuk/1ce-icons-for-plantuml/2.0.0/dist
!include v8_PUML/common.puml
!include v8_PUML/v8_Catalog.puml
!include v8_PUML/v8_Enum.puml"""

def generateOutput(filename, metadata):
    
    File = open(filename.strip(), 'w')
    File.write("@startuml 1C_ER")
    File.write(connectIcons())

    for m in metadata:
        
        File.write("\n")
        
        for metadataClass in metadata[m]:
            File.write("\n" + metadataClass.puml + "\n")

    File.write("\n@enduml")
    File.close()

def makeDiagram(params):
    
    metadataFilter = ['Catalog', 'Enum']
    metadata = {}

    # Найдем описание кончигурации
    srcPath = params.srcPath.strip()
    confFile = md.findConfFile(srcPath, "Configuration")

    rootNode = ETree.parse(confFile).getroot()

    for m in metadataFilter:
        metadata[m] = []
        metaclass = md.__dict__[m]
        for child in rootNode.iter(md.prefix() + m):
            metadataObject = metaclass(child.text)
            metadataObject.ini(srcPath)
            metadata[m].append(metadataObject)
    
    generateOutput(params.output, metadata)

if __name__ == "__main__":
   
    parser = createParser()
    namespace = parser.parse_args(sys.argv[1:])

    validateParams(namespace)
    makeDiagram(namespace)

