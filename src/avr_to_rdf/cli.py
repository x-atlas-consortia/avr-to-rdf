"""Command-line interface for AVR to RDF converter."""

from pathlib import Path

import click

from avr_to_rdf.pipeline.downloader import download_avr_data
from avr_to_rdf.pipeline.docs import (
    generate_schema_outputs,
    write_data_index_html,
    write_file_manifest,
    write_root_index_html,
)
from avr_to_rdf.pipeline.transformer import transform_linkml_yaml_to_json, transform_to_linkml_yaml
from avr_to_rdf.rdf.generator import generate_rdf_outputs


@click.group()
def main():
    """AVR to RDF Converter."""
    pass


@main.command()
@click.option(
    "--output",
    type=click.Path(),
   default="dist/data/avr-data.source.json",
    help="Output file for downloaded JSON data",
)
def download(output: str):
    """Download AVR data from the API."""
    click.echo(f"Downloading AVR data to {output}...")
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    download_avr_data(output_path)
    click.echo("Download complete!")


@main.command()
@click.option(
    "--input",
    type=click.Path(exists=True),
   default="dist/data/avr-data.source.json",
    help="Input JSON file",
)
@click.option(
    "--output",
    type=click.Path(),
   default="dist/data/avr-data.yaml",
    help="Output YAML file in LinkML format",
)
def convert(input: str, output: str):
    """Convert AVR JSON to LinkML YAML format."""
    click.echo(f"Converting {input} to LinkML YAML...")
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    transform_to_linkml_yaml(Path(input), output_path)
    click.echo(f"Conversion complete! Output: {output}")


@main.command()
@click.option(
    "--input",
    type=click.Path(exists=True),
   default="dist/data/avr-data.yaml",
    help="Input YAML file in LinkML format",
)
@click.option(
    "--output-dir",
    type=click.Path(),
   default="dist/data",
    help="Output directory for RDF files",
)
def rdf(input: str, output_dir: str):
    """Generate RDF outputs (Turtle, OWL, JSON-LD, N-Triples)."""
    click.echo(f"Generating RDF outputs from {input}...")
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    generate_rdf_outputs(Path(input), output_path)
    click.echo(f"RDF generation complete! Output: {output_dir}")


@main.command()
def generate():
    """Run full pipeline: generate schema docs, download, convert, and generate RDF."""
    click.echo("Running full AVR to RDF pipeline...")

    # Generate schema outputs
    click.echo("\n[1/5] Generating LinkML schema outputs...")
    schema_path = Path("src/avr_to_rdf/schema/avr.yaml")
    generate_schema_outputs(schema_path, Path("dist/schema"))
    click.echo("✓ Schema output generation complete")

    # Download
    click.echo("\n[2/5] Downloading AVR data...")
    download_path = Path("dist/data/avr-data.source.json")
    download_path.parent.mkdir(parents=True, exist_ok=True)
    download_avr_data(download_path)
    click.echo("✓ Download complete")
    
    # Convert
    click.echo("\n[3/5] Converting to LinkML YAML...")
    yaml_path = Path("dist/data/avr-data.yaml")
    transform_to_linkml_yaml(download_path, yaml_path)
    click.echo("✓ Conversion complete")

    # Convert YAML to LinkML JSON
    click.echo("\n[4/5] Converting LinkML YAML to JSON...")
    linkml_json_path = Path("dist/data/avr-data.json")
    transform_linkml_yaml_to_json(yaml_path, linkml_json_path)
    click.echo("✓ LinkML JSON generation complete")
    
    # Generate RDF
    click.echo("\n[5/5] Generating RDF outputs...")
    output_dir = Path("dist/data")
    generate_rdf_outputs(yaml_path, output_dir)
    click.echo("✓ RDF generation complete")

    # Generate the site landing pages at the dist root and section roots
    write_root_index_html(Path("dist"))
    write_data_index_html(Path("dist/data"))

    # Generate manifests for GitHub Pages-friendly file listings
    write_file_manifest(Path("dist/data"))
    write_file_manifest(Path("dist/schema"))
    write_file_manifest(Path("dist/schema/documentation"))
    
    # Write creation date
    from datetime import datetime
    creation_date_file = Path("dist/CREATION_DATE")
    creation_date_file.write_text(datetime.now().isoformat())
    click.echo(f"\n✓ Pipeline complete! Creation date recorded in {creation_date_file}")


if __name__ == "__main__":
    main()
