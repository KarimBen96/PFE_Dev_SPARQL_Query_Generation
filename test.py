from itertools import combinations
from Phases.Ontology_Exploration.Ontology_Exploration import *
from Phases.Mapping.Mapping import *
""""
onto = load_ontology('Uploaded_Files/hero.owl')
el=build_ontology(onto)
ontoS = OntologySchema(el,'hero')
onto_elems_necessary=get_onto_elems_necessary(['be','teacher','evaluated'],ontoS)
list= get_onto_elems_for_mapping(['be','teacher','Laboratory'], onto_elems_necessary)
a=mapping_How_complex(list)
for i in range (1,4):
    list = ngram_generation(['be','teacher','laboratory'],i)
    for j in list:
        print(j)
"""""
onto = load_ontology('Uploaded_Files/hero.owl')
el=build_ontology(onto)
ontoS = OntologySchema(el,'hero')
list= get_onto_elems_necessary(['be','grade'], ontoS)
list2= get_onto_elems_for_mapping(['be','grade'], list)
b,a=mapping_listing(list2)
print(b)
for i in a:
  print(i['onto_elem'].IRI)