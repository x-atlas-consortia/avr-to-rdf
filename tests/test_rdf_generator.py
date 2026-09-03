from pathlib import Path

import yaml
from rdflib import Graph, URIRef
from rdflib.namespace import RDF

from avr_to_rdf.rdf.generator import generate_rdf_outputs


def test_rdf_outputs_include_type_and_updated_namespaces(tmp_path: Path):
    input_yaml = tmp_path / "avr-data.yaml"
    output_dir = tmp_path / "out"
    input_yaml.write_text(
        yaml.safe_dump(
            {
                "antibodies": [
                    {
                        "antibody_hubmap_id": "avr:HBM123.TEST.001",
                        "clonality": "monoclonal",
                        "host": "Mouse",
                        "recommended": True,
                        "hgnc_id": "http://identifiers.org/hgnc/5",
                        "author_orcids": [
                            "https://orcid.org/0000-0002-1234-5678",
                            "https://orcid.org/0000-0002-8765-4321",
                        ],
                        "avr_pdf": "https://assets.hubmapconsortium.org/ffff00396c3a7ac2765990322767bd0c/FUT4_AVR_OMAP10.pdf",
                    }
                ]
            },
            sort_keys=False,
        )
    )

    generate_rdf_outputs(input_yaml, output_dir)

    graph = Graph()
    graph.parse(output_dir / "avr-data.ttl", format="turtle")

    instance = URIRef("https://purl.humanatlas.io/graph/avr#HBM123.TEST.001")
    antibody_type = URIRef("https://purl.humanatlas.io/schema/avr#Antibody")
    hgnc_object = URIRef("http://identifiers.org/hgnc/5")
    orcid_1 = URIRef("https://orcid.org/0000-0002-1234-5678")
    orcid_2 = URIRef("https://orcid.org/0000-0002-8765-4321")
    avr_pdf = URIRef(
        "https://assets.hubmapconsortium.org/ffff00396c3a7ac2765990322767bd0c/FUT4_AVR_OMAP10.pdf"
    )

    assert (instance, RDF.type, antibody_type) in graph
    assert hgnc_object in graph.objects(instance, URIRef("https://purl.humanatlas.io/schema/avr#hgnc_id"))
    assert orcid_1 in graph.objects(instance, URIRef("https://purl.humanatlas.io/schema/avr#author_orcids"))
    assert orcid_2 in graph.objects(instance, URIRef("https://purl.humanatlas.io/schema/avr#author_orcids"))
    assert avr_pdf in graph.objects(instance, URIRef("https://purl.humanatlas.io/schema/avr#avr_pdf"))
