import spacy
from lxml import etree as et


def get_doc(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    return doc


def get_entities(doc):
    ent_dict = {}
    for ent in doc.ents:
        if ent.label_ not in ent_dict:
            ent_dict[ent.label_] = [(ent.start, ent.text)]
        else:
            ent_dict[ent.label_].append((ent.start, ent.text))

    return ent_dict


def get_dependencies(doc):
    return [(idx, (token.dep_, token.head.i, token.head, token)) for idx, token in enumerate(doc)]


def generate_xml(text):
    doc = get_doc(text)
    ent_dict, dependencies = get_entities(doc), get_dependencies(doc)
    root = et.Element("root")
    nes = et.SubElement(root, 'NamedEntities')
    deps = et.SubElement(root, 'Dependencies')

    for k, v in ent_dict.items():
        ne = et.SubElement(nes, 'named_ent', attrib={'type': k})
        for pair in v:
            e = et.SubElement(ne, 'ent', attrib={'idx': str(pair[0])})
            e.text = str(pair[1])

    for d in dependencies:
        node = et.SubElement(deps, 'dep', attrib={'type': str(d[1][0])})
        gov = et.SubElement(node, 'governor', attrib={'idx': str(d[1][1])})
        gov.text = str(d[1][2])
        dep = et.SubElement(node, 'dependant', attrib={'idx': str(d[0])})
        dep.text = str(d[1][3])

    return et.tostring(root).decode('utf-8')
