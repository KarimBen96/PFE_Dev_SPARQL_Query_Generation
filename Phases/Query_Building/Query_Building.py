#
#               This is the Query Building Phase
#



#
#               This is the Query Building Phase
#



def query_builder(label, iri1=None, iri2=None, iri3=None):
    if label == 'definition':
        return definition_query_build(iri1)
    elif label == 'entity_list':
        return entity_list_query_build(iri1)
    elif label == 'property_list':
        return property_list_query_build(iri1)
    elif label == 'Object_property_test':
        return object_propoerty_test_build(iri1, iri2, iri3)
    elif label == 'Object_property_find' and iri2 is not None:
        return object_property_find_build1(iri1, iri2)
    elif label == 'Object_property_find':
        return object_property_find_build2(iri1)
    elif label == 'property_hierarchy':
        return hierarchy_Property_Property(iri1, iri2)
    elif label == 'Entity_hierarchy':
        return hierarchy_Class_Class(iri1, iri2)
    elif label == 'How_complex':
        return how_complex_build(iri1)
    elif label == 'type_belong':
        return Type_Object_Class(iri1, iri2)


def definition_query_build(iri):
    part1 = f"<{iri}> rdfs:isDefinedBy ?x"
    part2 = f"<{iri}> rdfs:comment ?x"
    query = "SELECT ?x WHERE {{" + part1 + "}UNION {" + part2 + "}}"
    return query


def entity_list_query_build(iri):
    cond = f"?x rdfs:subClassOf <{iri}>"
    query = "SELECT ?x WHERE {" + cond + "}"
    return query


def property_list_query_build(iri):
    cond = f"?x rdfs:subPropertyOf <{iri}>"
    query = "SELECT ?x WHERE {" + cond + "}"
    return query


def object_propoerty_test_build(prop_iri, iri1, iri2):
    cond1 = f"<{prop_iri}> rdfs:domain <{iri1}>; rdfs:range ?C"
    cond2 = f"?C rdfs:subClassOf <{iri2}> "
    query = "ASK{" + cond1 + "," + cond2 + "}"
    return query


def object_property_find_build1(iri1, iri2):
    cond1 = f"?x rdfs:domain <{iri1}>; rdfs:range ?C"
    cond2 = f"?C rdfs:subClassOf <{iri2}> "
    query = "SELECT ?x WHERE {" + cond1 + ";" + cond2 + "}"
    return query


def object_property_find_build2(iri_prop):
    cond = f" x? <{iri_prop} ?y >"
    query = "SELECT ?x y? WHERE{" + cond + "}"
    return query


def hierarchy_Class_Class(class1_iri, class2_iri):
    cond = f"<{class1_iri}> rdfs:subClassOf <{class2_iri}>"
    query = "Ask{" + cond + "}"
    return query


def hierarchy_Property_Property(prop1_iri, prop2_iri):
    cond = f'<{prop1_iri}> rdfs:subPropertyOf <{prop2_iri}>'
    query = "Ask{" + cond + "}"
    return query


def Type_Object_Class(obj_iri, class_iri):
    cond = f'<{obj_iri}> rdfs:Type <{class_iri}>'
    query = "Ask{" + cond + "}"
    return query


def how_complex_build(prop_iri):
    cond1 = f'<{prop_iri}> rdfs:domain ?x ; rdfs:range ?y'
    cond2 = f'<{prop_iri}> rdfs:comment  ?z'
    query = "SELECT ?x ?y ?z WHERE {{" + cond1 + " }UNION {" + cond2 + "}}"
    return query
