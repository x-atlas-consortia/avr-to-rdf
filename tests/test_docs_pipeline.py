from pathlib import Path

from avr_to_rdf.pipeline.docs import generate_schema_outputs, write_data_index_html, write_root_index_html


def test_schema_outputs_place_docs_in_subdirectory_and_convert_markdown(tmp_path: Path):
    schema_path = Path("src/avr_to_rdf/schema/avr.yaml")
    output_dir = tmp_path / "schema"

    generate_schema_outputs(schema_path, output_dir)

    assert (output_dir / "index.html").exists()
    assert (output_dir / "schema.yaml").exists()
    assert (output_dir / "schema.json").exists()
    assert (output_dir / "schema.context.jsonld").exists()
    assert (output_dir / "schema.owl").exists()
    assert (output_dir / "schema.mmd").exists()
    assert (output_dir / "schema.svg").exists()
    assert (output_dir / "schema.png").exists()

    documentation_dir = output_dir / "documentation"
    assert documentation_dir.exists()
    assert (documentation_dir / "index.html").exists()
    assert (documentation_dir / "Antibody.html").exists()
    assert (documentation_dir / "schema.erd.html").exists()
    assert (documentation_dir / "schema.erd.mmd").exists()
    assert (documentation_dir / "schema.erd.svg").exists()
    assert (documentation_dir / "schema.erd.png").exists()
    assert not list(documentation_dir.rglob("*.md"))
    assert not (output_dir / "Antibody.md").exists()


def test_root_and_data_indexes_are_written(tmp_path: Path):
    root_dir = tmp_path / "dist"
    data_dir = root_dir / "data"
    schema_dir = root_dir / "schema"
    data_dir.mkdir(parents=True)
    schema_dir.mkdir(parents=True)

    write_root_index_html(root_dir)
    write_data_index_html(data_dir)

    assert (root_dir / "index.html").exists()
    assert (data_dir / "index.html").exists()
