"""Transform AVR JSON data to LinkML YAML format."""

import json
import re
from pathlib import Path
from typing import Any, Dict, Optional

import requests
import yaml


HRA_GRAPH_URL = "https://cdn.humanatlas.io/digital-objects/collection/hra/latest/graph.json"
AVR_DATA_IRI = "https://purl.humanatlas.io/graph/avr"
AVR_SCHEMA_CONTEXT_URL = "https://cdn.humanatlas.io/digital-objects/schema/avr/latest/assets/schema.context.jsonld"
AVR_JSON_SCHEMA_URL = "https://cdn.humanatlas.io/digital-objects/schema/avr/latest/assets/schema.json"


def split_orcids(value: str) -> list[str]:
    """Split a comma/semicolon separated ORCID field into ORCID IRIs."""
    items = [item.strip() for item in value.replace(";", ",").split(",")]
    return [f"https://orcid.org/{item}" for item in items if item]


def normalize_to_curie(value: str, prefix: str, raw_prefix: Optional[str] = None) -> str:
    clean = value.strip()
    if clean.startswith("http://") or clean.startswith("https://") or clean.startswith(f"{prefix}:"):
        return clean
    if raw_prefix and clean.startswith(f"{raw_prefix}:"):
        clean = clean.removeprefix(f"{raw_prefix}:")
    return f"{prefix}:{clean}"


def normalize_to_iri(
    value: str, base_iri: str, prefix: Optional[str] = None, raw_prefix: Optional[str] = None
) -> str:
    clean = value.strip()
    if clean.startswith("http://") or clean.startswith("https://"):
        return clean
    if prefix and clean.startswith(f"{prefix}:"):
        clean = clean.removeprefix(f"{prefix}:")
    if raw_prefix and clean.startswith(f"{raw_prefix}:"):
        clean = clean.removeprefix(f"{raw_prefix}:")
    return f"{base_iri}{clean}"


def normalize_boolean(value: Any) -> Optional[bool]:
    """Normalize common Yes/No or boolean-like values to a Python bool."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        cleaned = value.strip().lower()
        if cleaned in {"yes", "y", "true", "1"}:
            return True
        if cleaned in {"no", "n", "false", "0"}:
            return False
    return None


def normalize_integer(value: Any, field_name: str) -> int:
    """Normalize integer-like API values to Python int."""
    if isinstance(value, bool):
        raise ValueError(f"Invalid integer value for {field_name}: {value}")
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if value.is_integer():
            return int(value)
        raise ValueError(f"Invalid integer value for {field_name}: {value}")
    if isinstance(value, str):
        cleaned = value.strip()
        if re.fullmatch(r"[+-]?\d+", cleaned):
            return int(cleaned)
    raise ValueError(f"Invalid integer value for {field_name}: {value}")


def _extract_omap_number(value: str) -> Optional[str]:
    match = re.search(r"(\d+)", value)
    if not match:
        return None
    return str(int(match.group(1)))


def _strip_purl_version(member_url: str) -> str:
    return re.sub(r"/v\d+(?:\.\d+)*$", "", member_url)


def _resolve_purl(member_url: str) -> Optional[str]:
    response = requests.get(member_url, timeout=30, allow_redirects=True)
    if response.ok and response.url:
        return response.url
    return None


def load_omap_purl_lookup(graph_url: str = HRA_GRAPH_URL) -> Dict[str, str]:
    """Load OMAP ID number -> canonical PURL (versionless) map from HRA collection graph."""
    response = requests.get(graph_url, timeout=30)
    response.raise_for_status()
    payload = response.json()
    had_member = payload.get("metadata", {}).get("had_member", [])

    lookup: Dict[str, str] = {}
    prefix = "https://purl.humanatlas.io/omap/"
    for member in had_member:
        if not isinstance(member, str) or not member.startswith(prefix):
            continue
        segment = member[len(prefix):]
        if "-" not in segment:
            continue
        omap_number = segment.split("-", 1)[0]
        if not omap_number.isdigit():
            continue
        normalized_number = str(int(omap_number))
        if normalized_number not in lookup:
            versionless_member = _strip_purl_version(member)
            resolved = _resolve_purl(versionless_member)
            lookup[normalized_number] = _strip_purl_version(resolved or versionless_member)
    return lookup


def normalize_antibody(antibody: Dict[str, Any], omap_purl_lookup: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Normalize an antibody record for LinkML.
    
    Args:
        antibody: Raw antibody data from API
         
    Returns:
        Normalized antibody data
    """
    normalized = {}
    
    for key, value in antibody.items():
        if value is None or value == "":
            continue
        if key in {"recommended", "recombinant", "senescence_specific"}:
            boolean_value = normalize_boolean(value)
            if boolean_value is not None:
                normalized[key] = boolean_value
                continue
        if key in {"cycle_number", "dilution_factor"}:
            normalized[key] = normalize_integer(value, key)
            continue
        if key == "antibody_hubmap_id" and isinstance(value, str):
            normalized[key] = value if value.startswith("avr:") else f"avr:{value.strip()}"
            continue
        if key == "hgnc_id" and isinstance(value, str):
            normalized[key] = normalize_to_iri(
                value, "http://identifiers.org/hgnc/", prefix="hgnc", raw_prefix="HGNC"
            )
            continue
        if key == "uniprot_accession_number" and isinstance(value, str):
            normalized[key] = normalize_to_iri(
                value, "http://purl.uniprot.org/uniprot/", prefix="uniprot"
            )
            continue
        if key == "rrid" and isinstance(value, str):
            normalized[key] = normalize_to_iri(
                value, "https://identifiers.org/RRID:", prefix="rrid", raw_prefix="RRID"
            )
            continue
        if key == "organ_uberon_id" and isinstance(value, str):
            normalized[key] = normalize_to_iri(
                value, "http://purl.obolibrary.org/obo/UBERON_", prefix="uberon", raw_prefix="UBERON"
            )
            continue
        if key in {"protocol_doi", "manuscript_doi"} and isinstance(value, str):
            doi = value.strip().removeprefix("https://doi.org/").removeprefix("http://doi.org/")
            normalized[key] = f"https://doi.org/{doi}" if doi else value.strip()
            continue
        if key == "author_orcids" and isinstance(value, str):
            normalized[key] = split_orcids(value)
            continue
        if key == "author_orcids" and isinstance(value, list):
            normalized[key] = [f"https://orcid.org/{item.strip()}" for item in value if item and item.strip()]
            continue
        normalized[key] = value.strip() if isinstance(value, str) else value
    
    avr_pdf_uuid = normalized.get("avr_pdf_uuid")
    avr_pdf_filename = normalized.get("avr_pdf_filename")
    if isinstance(avr_pdf_uuid, str) and isinstance(avr_pdf_filename, str):
        if avr_pdf_uuid.strip() and avr_pdf_filename.strip():
            normalized["avr_pdf"] = (
                f"https://assets.hubmapconsortium.org/{avr_pdf_uuid.strip()}/{avr_pdf_filename.strip()}"
            )

    raw_omap_value = None
    if isinstance(antibody.get("omap"), str):
        raw_omap_value = antibody["omap"].strip()
    elif isinstance(antibody.get("omap_id"), str):
        raw_omap_value = antibody["omap_id"].strip()

    if raw_omap_value:
        normalized["omap"] = raw_omap_value
        if raw_omap_value.startswith("http://") or raw_omap_value.startswith("https://"):
            normalized["omap_id"] = raw_omap_value
        elif omap_purl_lookup:
            omap_number = _extract_omap_number(raw_omap_value)
            if omap_number and omap_number in omap_purl_lookup:
                normalized["omap_id"] = omap_purl_lookup[omap_number]

    return normalized


def transform_to_linkml_yaml(input_path: Path, output_path: Path) -> None:
    """
    Transform AVR JSON data to LinkML YAML format.
    
    Args:
        input_path: Path to input JSON file
        output_path: Path to output YAML file
    """
    print(f"Transforming {input_path} to LinkML YAML...")
    
    # Load JSON data
    with open(input_path, "r") as f:
        data = json.load(f)
    
    antibodies = data.get("antibodies", [])
    
    omap_purl_lookup = load_omap_purl_lookup()

    # Normalize all antibodies
    normalized_antibodies = [normalize_antibody(ab, omap_purl_lookup=omap_purl_lookup) for ab in antibodies]
    
    # Create LinkML-compatible structure
    linkml_data = {
        "antibodies": normalized_antibodies
    }
    
    # Save to YAML
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        yaml.dump(linkml_data, f, default_flow_style=False, sort_keys=False)
    
    print(f"Transformed {len(normalized_antibodies)} antibodies to {output_path}")


def transform_linkml_yaml_to_json(input_yaml_path: Path, output_json_path: Path, schema_path: Optional[Path] = None) -> None:
    """Convert LinkML YAML instance data to canonical LinkML JSON."""
    from linkml.generators.pythongen import PythonGenerator
    from linkml_runtime.dumpers import json_dumper
    from linkml_runtime.loaders import yaml_loader

    if schema_path is None:
        schema_path = Path(__file__).parent.parent / "schema" / "avr.yaml"

    print(f"Converting {input_yaml_path} to LinkML JSON...")
    module = PythonGenerator(str(schema_path)).compile_module()
    root_class_name = "AntibodyValidationReportCollection"
    target_class = module.__dict__[root_class_name]
    instance_obj = yaml_loader.load(str(input_yaml_path), target_class=target_class)

    output_json_path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.loads(json_dumper.dumps(instance_obj))
    enriched_payload = {
        "iri": AVR_DATA_IRI,
        "@context": AVR_SCHEMA_CONTEXT_URL,
        "$schema": AVR_JSON_SCHEMA_URL,
        "@type": payload.get("@type", root_class_name),
    }
    for key, value in payload.items():
        if key not in enriched_payload:
            enriched_payload[key] = value
    output_json_path.write_text(json.dumps(enriched_payload, indent=2) + "\n")
    print(f"Generated LinkML JSON: {output_json_path}")
