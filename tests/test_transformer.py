import json
from pathlib import Path

import yaml

from avr_to_rdf.pipeline.transformer import (
    load_omap_purl_lookup,
    normalize_antibody,
    transform_linkml_yaml_to_json,
)


def test_normalize_antibody_prefixes_id_and_splits_orcids():
    record = {
        "antibody_hubmap_id": "HBM123.TEST.001",
        "author_orcids": "0000-0002-1234-5678, 0000-0002-9999-000X",
        "recommended": "Yes",
    }
    normalized = normalize_antibody(record)
    assert normalized["antibody_hubmap_id"] == "avr:HBM123.TEST.001"
    assert normalized["recommended"] is True
    assert normalized["author_orcids"] == [
        "https://orcid.org/0000-0002-1234-5678",
        "https://orcid.org/0000-0002-9999-000X",
    ]


def test_normalize_antibody_derives_avr_pdf_url():
    record = {
        "avr_pdf_uuid": "ffff00396c3a7ac2765990322767bd0c",
        "avr_pdf_filename": "FUT4_AVR_OMAP10.pdf",
    }
    normalized = normalize_antibody(record)
    assert normalized["avr_pdf"] == (
        "https://assets.hubmapconsortium.org/"
        "ffff00396c3a7ac2765990322767bd0c/FUT4_AVR_OMAP10.pdf"
    )


def test_normalize_antibody_converts_identifier_fields_to_iris():
    record = {
        "hgnc_id": "HGNC:5",
        "uniprot_accession_number": "P12345",
        "rrid": "RRID:AB_123",
        "organ_uberon_id": "UBERON:0002107",
    }
    normalized = normalize_antibody(record)
    assert normalized["hgnc_id"] == "http://identifiers.org/hgnc/5"
    assert normalized["uniprot_accession_number"] == "http://purl.uniprot.org/uniprot/P12345"
    assert normalized["rrid"] == "https://identifiers.org/RRID:AB_123"
    assert normalized["organ_uberon_id"] == "http://purl.obolibrary.org/obo/UBERON_0002107"


def test_normalize_antibody_converts_integer_fields_and_sets_omap_id():
    record = {
        "omap_id": "OMAP-14",
        "cycle_number": "2",
        "dilution_factor": "250",
    }
    normalized = normalize_antibody(
        record,
        omap_purl_lookup={"14": "https://purl.humanatlas.io/2d-ftu/kidney-ascending-thin-loop-of-henle"},
    )
    assert normalized["cycle_number"] == 2
    assert normalized["dilution_factor"] == 250
    assert normalized["omap"] == "OMAP-14"
    assert normalized["omap_id"] == "https://purl.humanatlas.io/2d-ftu/kidney-ascending-thin-loop-of-henle"


def test_load_omap_purl_lookup_uses_first_had_member_and_strips_version(monkeypatch):
    class Response:
        def __init__(self, payload=None, url=None, ok=True):
            self._payload = payload
            self.url = url
            self.ok = ok

        def raise_for_status(self):
            return None

        def json(self):
            return self._payload

    def fake_get(url, timeout=30, allow_redirects=False):
        if url == "https://example.org/graph.json":
            return Response(
                payload={
                    "metadata": {
                        "had_member": [
                            "https://purl.humanatlas.io/omap/14-kidney-cycif/v1.1",
                            "https://purl.humanatlas.io/omap/14-kidney-other/v1.0",
                        ]
                    }
                }
            )
        if url == "https://purl.humanatlas.io/omap/14-kidney-cycif":
            return Response(url="https://purl.humanatlas.io/2d-ftu/kidney-ascending-thin-loop-of-henle/v1.4")
        raise AssertionError(f"Unexpected URL: {url}")

    monkeypatch.setattr("avr_to_rdf.pipeline.transformer.requests.get", fake_get)

    lookup = load_omap_purl_lookup("https://example.org/graph.json")

    assert lookup["14"] == "https://purl.humanatlas.io/2d-ftu/kidney-ascending-thin-loop-of-henle"


def test_transform_linkml_yaml_to_json_generates_json_output(tmp_path: Path):
    input_yaml = tmp_path / "avr-data.yaml"
    output_json = tmp_path / "avr-data.json"
    input_yaml.write_text(
        yaml.safe_dump(
            {
                "antibodies": [
                    {
                        "antibody_hubmap_id": "avr:HBM123.TEST.001",
                        "clonality": "monoclonal",
                        "host": "Mouse",
                        "recommended": True,
                    }
                ]
            },
            sort_keys=False,
        )
    )

    transform_linkml_yaml_to_json(input_yaml, output_json)
    payload = json.loads(output_json.read_text())

    assert payload["iri"] == "https://purl.humanatlas.io/graph/avr"
    assert (
        payload["@context"]
        == "https://cdn.humanatlas.io/digital-objects/schema/avr/latest/assets/schema.context.jsonld"
    )
    assert payload["$schema"] == "https://cdn.humanatlas.io/digital-objects/schema/avr/latest/assets/schema.json"
    assert payload["@type"] == "AntibodyValidationReportCollection"
    assert "antibodies" in payload
    assert payload["antibodies"][0]["antibody_hubmap_id"] == "avr:HBM123.TEST.001"
