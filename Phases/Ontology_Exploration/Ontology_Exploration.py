#
#               This is the Ontology Exploration Phase
#



from owlready2 import *
from enum import Enum
from Phases.Mapping import Mapping as mapping




class Type(Enum):
    CLASS = 1
    OBJECT_PROPERTY = 2
    DATA_PROPERTY = 3
    ANNOTATION_PROPERTY = 4


class OntologyElement:
    """
    - processed_name: is the list obtained by the function (sep_str_onto_elem)
    - glove_list: is a list of a top 5 or top 10 nearest words
    """

    def __init__(self, type_, name, iri, processed_name=None, glove_list=None):
        self.type = type_
        self.name = name
        self.IRI = iri
        self.processed_name = processed_name
        self.glove_list = glove_list

    def to_print_onto_elem(self):
        return '{} - {} - {}'.format(self.name, self.IRI, self.type)



class OntologySchema:
    """

    """

    def __init__(self, onto_elems_list, name=None):
        self.name = name
        self.onto_elems_list = onto_elems_list

    def to_print_onto_elems(self):
        return [item.to_print_onto_elem() for item in self.onto_elems_list]

    def get_elems_by_type(self, type_):
        return [item for item in self.onto_elems_list if item.type == type_]




def load_ontology(onto_path):
    onto = get_ontology(onto_path).load()
    return onto



def build_ontology(onto):
    """

    """

    onto_list = []

    for i in onto.classes():
        concept = OntologyElement(Type.CLASS, re.findall('\.([^\.]*$)', str(i))[0], i.iri)
        onto_list.append(concept)
    for i in onto.object_properties():
        object_property = OntologyElement(Type.OBJECT_PROPERTY, re.findall('\.([^\.]*$)', str(i))[0], i.iri)
        onto_list.append(object_property)
    for i in onto.data_properties():
        data_property = OntologyElement(Type.DATA_PROPERTY, re.findall('\.([^\.]*$)', str(i))[0], i.iri)
        onto_list.append(data_property)
    for i in onto.annotation_properties():
        annot = OntologyElement(Type.ANNOTATION_PROPERTY, re.findall('\.([^\.]*$)', str(i))[0], i.iri)
        onto_list.append(annot)

    for item in onto_list:
        item.processed_name = mapping.sep_str_onto_elem(item.name)

    return onto_list
