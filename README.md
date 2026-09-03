# AVR to RDF Converter

Convert Antibody Validation Report (AVR) records from the HuBMAP and SenNet consortia into validated, linked open data in RDF format.

Publishing targets:
- Schema base IRI: `https://purl.humanatlas.io/schema/avr`
- Schema property namespace: `https://purl.humanatlas.io/schema/avr#` (`avro:`)
- Data graph base IRI: `https://purl.humanatlas.io/graph/avr`

## Installation

```bash
pip install -e .
```

Or with poetry:

```bash
poetry install
```

## Usage

```bash
avr-to-rdf download   # Download source data from AVR API
avr-to-rdf convert    # Convert source JSON to LinkML YAML
avr-to-rdf generate   # Generate full output and documentation under dist/
```

Generated website artifacts are written to `dist/` and published to the `gh-pages` branch via GitHub Actions, where they are copied into a `docs/` folder for GitHub Pages hosting.

## Project Structure

- `src/avr_to_rdf/` - Python package
  - `cli.py` - CLI entry point
  - `schema/` - LinkML schema definitions
  - `pipeline/` - Data download, validation, and transformation
  - `rdf/` - RDF generation utilities
- `dist/` - Generated output (schema and data); not committed to the repository
  - `dist/schema/documentation/` - Generated LinkML schema documentation pages (HTML)
- `tests/` - Test suite

## References

- [AVR SOP](https://zenodo.org/records/20543394)
- [AVR Documentation](https://docs.hubmapconsortium.org/avr/index.html)
- [AVR TSV Format](https://docs.hubmapconsortium.org/avr/tsv-format-v2.html)
- [AVR API](https://avr.xconsortia.org/antibodies)
- [OpenAPI Spec](https://github.com/x-atlas-consortia/avr-ui/blob/main/antibody-api-spec.yaml)
- [HRA DO Processor](https://github.com/hubmapconsortium/hra-do-processor)
- [HRA data processing paper](https://www.nature.com/articles/s41597-025-05183-6)
