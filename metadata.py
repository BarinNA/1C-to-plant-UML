import xml.etree.ElementTree as ET
import os

class Catalog:

    def __init__(self, name) -> None:
        self.name = name
        self.properties = []
        self.connections = []
        self.relation = []

    def __repr__(self) -> str:
        return f'{self.name}'

    def ini(self, path):

        # Ищем файл с конфигурацией
        confFile = findConfFile(path, self.name)

        # разбирем его и заполняем данные объекта
        root = ET.parse(confFile).getroot()

        # Заполним владельца
        element_Owner = findElement(root, "Catalog.Properties.Owners")
        if element_Owner != None and len(element_Owner):

            type1C = type1CAlias(element_Owner[0].text)
            owner = Property("Владелец", type1C["type"], type1C["typeName"], True)
            self.properties.append(owner)

        # заполним реквизиты
        for attibute in root.iter(prefix() + "Attribute"):

            prop = parseAttribute(attibute)
            self.properties.append(prop)

        # заполним связи
        for prop in self.properties:
            if prop.index:
                connect = Connection(self.name, prop.typeName, prop.name)
                self.connections.append(connect)


    @property
    def puml(self):
        n = '\n\t'
        strProrerties = pulm_getProperties(self.properties)

        strCatalog = f"_Справочник({repr(self)}){{{n}{strProrerties}{n}}}"
        
        strConnections = '\n'.join(i.puml for i in self.connections)

        return strCatalog + "\n" + strConnections
    
class Document:

    def __init__(self, name) -> None:
        self.name = name
        self.properties = []

    def __repr__(self) -> str:
        return f'Документ.{self.name}'

    @property
    def puml(self):
        return f"object {repr(self)}"

class Enum:

    def __init__(self, name) -> None:
        self.name = name
        self.values = []

    def ini(self, path):
        
        # Ищем файл с конфигурацией
        confFile = findConfFile(path, self.name)

        # разбирем его и заполняем данные объекта
        root = ET.parse(confFile).getroot()

        for el in root.iter(f'{prefix()}EnumValue'):
            self.values.append(parsePropertie(el, "Name"))

    @property    
    def puml(self):
        n = '\n\t'
        strProrerties = pulm_getValues(self.values, n)
        return f"_Перечисление({self.name}){{{n}{strProrerties}{n}}}"     

class Property:

    def __init__(self, name, type, typeName = "", index = False) -> None:
        self.name = name
        self.type = type
        self.typeName = typeName
        self.index = index

    @property
    def puml(self):
        return f'{self.name}: {self.type}'

class Connection:

    def __init__(self, source, reciever, sourceProperty = "", recieverPropertie = "") -> None:
        self.source = source
        self.reciever = reciever
        self.sourceProperty = sourceProperty
        self.recieverPropertie = recieverPropertie

    @property
    def puml(self):

        propertieStr = lambda a: f"::{a}" if a != "" else ''
        return f'{self.source}{propertieStr(self.sourceProperty)} -> {self.reciever}{self.recieverPropertie}' 
    
              
def findConfFile(path, name):

    for root, dirs, files in os.walk(path):
        
        for file in files:
            if file == name + ".xml":
                return os.path.join(path, file)

        for dir in dirs:
            pathToFile = os.path.join(path, dir)
            result = findConfFile(pathToFile, name)

            if result != None:
                return result

    return None                

def prefix():

    return "{http://v8.1c.ru/8.3/MDClasses}"

def typePrefix():
    return '{http://v8.1c.ru/8.1/data/core}'

def type1CAlias(type):
    
    Alias1c = {"type": type, "typeName": "", "index": False}

    # разберем базовые типы
    if type.find('v8:') != -1 or type.find('xs:') != -1:
        
        types = {"xs:boolean": "Булево", 
                "xs:string": "Строка", 
                "xs:decimal": "Число", 
                "v8:ValueStorage": "ХранилищеЗначений"}

        type1C = types.get(type)

        if type1C == None:
            return Alias1c
        else:
            Alias1c['type'] = type1C
            return Alias1c

    # разберем ссылочные типы
    metaType = {"cfg:EnumRef": "Перечисление",
                "cfg:CatalogRef": "Справочник",
                "Catalog": "Справочник",
                "cfg:DocumentRef": "Документ",
                "Document": "Документ"}

    for key, value in metaType.items():
        if type.find(key) != -1:
           
            Alias1c['type'] = type.replace(key, value)
            Alias1c["index"] = True
            Alias1c["typeName"] = type.replace(f"{key}.", "") 

            return Alias1c

    return Alias1c
    
def parseAttribute(attribute, fienlds = None):
    # /attribute/Properties/{protertie}
        
    propertyElement = attribute.find(f"{prefix()}Properties")
    name = propertyElement.find(f"{prefix()}Name").text
    type = propertyElement.find(f"{prefix()}Type").find(f"{typePrefix()}Type").text

    type1C = type1CAlias(type)

    return Property(name, type1C['type'], type1C['typeName'], type1C['index'])

def parsePropertie(element, field):

    element_Properties = element.find(f"{prefix()}Properties")
    
    return element_Properties.find(f"{prefix()}{field}").text

def findElement(root, path):
    # путь в формате Catalog.Properties.Owners

    element = root

    for el in path.split('.'):
        if element == None:
            return None
        else:
            element = element.find(f"{prefix()}{el}")

    return element        

def pulm_getProperties(properties):
    n = '\n\t'
    return f'{n}'.join(i.puml for i in properties)

def pulm_getValues(properties, separator):
    return f'{separator}'.join(i for i in properties)