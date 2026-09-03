"""Generate RDF outputs from LinkML YAML data using LinkML runtime."""

from pathlib import Path
from typing import Optional


def generate_rdf_outputs(input_yaml_path: Path, output_dir: Path, schema_path: Optional[Path] = None) -> None:
    """
    Generate RDF outputs (Turtle, OWL/XML, JSON-LD, N-Triples) from LinkML YAML.

    Args:
        input_yaml_path: Path to input YAML file in LinkML instance format
        output_dir: Directory to save RDF outputs
        schema_path: Path to LinkML schema (uses default if not provided)
    """
    from linkml.generators.pythongen import PythonGenerator
    from linkml_runtime.dumpers import rdflib_dumper
    from linkml_runtime.loaders import yaml_loader
    from linkml_runtime.utils.schemaview import SchemaView

    output_dir.mkdir(parents=True, exist_ok=True)
    if schema_path is None:
        schema_path = Path(__file__).parent.parent / "schema" / "avr.yaml"

    print(f"Generating RDF outputs from {input_yaml_path}")
    print(f"Using schema: {schema_path}")
    print(f"Output directory: {output_dir}")

    module = PythonGenerator(str(schema_path)).compile_module()
    sv = SchemaView(str(schema_path))
    root_class_name = "AntibodyValidationReportCollection"
    target_class = module.__dict__[root_class_name]
    instance_obj = yaml_loader.load(str(input_yaml_path), target_class=target_class)

    formats = [
        ("ttl", "turtle", "Turtle"),
        ("jsonld", "json-ld", "JSON-LD"),
        ("owl", "xml", "OWL/XML"),
        ("nt", "nt", "N-Triples"),
    ]

    for extension, emit_fmt, display_name in formats:
        output_file = output_dir / f"avr-data.{extension}"
        print(f"\n  Generating {display_name} ({extension})...")
        try:
            rdflib_dumper.dump(instance_obj, str(output_file), schemaview=sv, fmt=emit_fmt)
            print(f"    ✓ Generated {output_file} using LinkML")
        except Exception as exc:
            raise RuntimeError(f"Failed generating {display_name} with LinkML: {exc}") from exc

    print("\n✓ RDF generation complete!")
