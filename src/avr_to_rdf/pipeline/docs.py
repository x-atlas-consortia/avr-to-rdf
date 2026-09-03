"""Helpers for generated docs output."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

from linkml.generators.docgen import DocGenerator
from linkml.generators.erdiagramgen import ERDiagramGenerator
from linkml.generators.jsonldcontextgen import ContextGenerator
from linkml.generators.jsonschemagen import JsonSchemaGenerator
from linkml.generators.owlgen import OwlSchemaGenerator
from markdown_it import MarkdownIt


def write_file_manifest(directory: Path, manifest_name: str = "files.json") -> None:
    """Write a simple JSON manifest of files in a generated docs directory."""
    files = sorted(
        path.name
        for path in directory.iterdir()
        if path.is_file() and path.name not in {manifest_name}
    )
    manifest_path = directory / manifest_name
    manifest_path.write_text(json.dumps({"files": files}, indent=2))


def _write_html(path: Path, html: str) -> None:
    path.write_text(html)


def write_root_index_html(output_dir: Path) -> None:
    """Write the site landing page."""
    _write_html(
        output_dir / "index.html",
        """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Antibody Validation Report (AVR) to RDF - Linked Open Data</title>
  <style>
    body { font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif; line-height: 1.6; color: #333; background: linear-gradient(135deg,#667eea 0%,#764ba2 100%); min-height: 100vh; padding: 20px; }
    .container { max-width: 1000px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 10px 40px rgba(0,0,0,.1); }
    h1 { color: #667eea; font-size: 3em; margin-bottom: 10px; text-align: center; }
    .subtitle, .tagline { text-align: center; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit,minmax(300px,1fr)); gap: 30px; margin: 2rem 0; }
    .card { background: linear-gradient(135deg,#667eea 0%,#764ba2 100%); color: white; padding: 30px; border-radius: 8px; text-align: center; }
    .card a { display: inline-block; background: white; color: #667eea; padding: 10px 20px; border-radius: 4px; text-decoration: none; font-weight: bold; }
    .info-section { background: #f0f4ff; border-left: 4px solid #667eea; padding: 24px; border-radius: 4px; margin-top: 2rem; }
    code { background: #f4f4f4; padding: 0.1rem 0.3rem; border-radius: 4px; }
  </style>
</head>
<body>
  <div class="container">
    <h1>Antibody Validation Report (AVR) to RDF</h1>
    <p class="subtitle">Antibody Validation Report</p>
    <p class="tagline">Converting biomedical data to linked open data for the Semantic Web</p>

    <div class="info-section">
      <p><strong>Schema:</strong> <code>https://purl.humanatlas.io/schema/avr</code></p>
      <p><strong>Schema properties:</strong> <code>https://purl.humanatlas.io/schema/avr#</code> (<code>avro:</code>)</p>
      <p><strong>Data graph:</strong> <code>https://purl.humanatlas.io/graph/avr</code></p>
    </div>

    <div class="grid">
      <div class="card">
        <h2>Schema</h2>
        <p>LinkML schema definitions and documentation.</p>
        <a href="./schema/">Browse Schema →</a>
      </div>
      <div class="card">
        <h2>Data</h2>
        <p>Converted antibody validation data in RDF and structured formats.</p>
        <a href="./data/">Browse Data →</a>
      </div>
    </div>
  </div>
</body>
</html>
""",
    )


def write_data_index_html(output_dir: Path) -> None:
    """Write the data landing page."""
    _write_html(
        output_dir / "index.html",
        """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AVR Data Resources</title>
  <style>
    body { max-width: 1000px; margin: 2rem auto; padding: 0 1rem; font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif; line-height: 1.6; color: #222; }
    a { color: #2f4fc2; }
    .info-box { background: #f0f4ff; border-left: 4px solid #667eea; padding: 20px; border-radius: 4px; margin-bottom: 20px; }
    .resource-grid { display: grid; grid-template-columns: repeat(auto-fit,minmax(220px,1fr)); gap: 16px; }
    .resource-card { border: 2px solid #eee; border-radius: 6px; padding: 16px; background: #fff; }
    .resource-card a { display: inline-block; text-decoration: none; color: white; background: #667eea; padding: 6px 12px; border-radius: 4px; font-weight: 500; }
    .file-list { list-style: none; background: #f5f5f5; padding: 20px; border-radius: 4px; border-left: 4px solid #667eea; }
    .file-list li { margin: 8px 0; padding: 8px; background: white; border-radius: 4px; display: flex; justify-content: space-between; align-items: center; }
    .file-type { display: inline-block; padding: 4px 8px; background: #667eea; color: white; border-radius: 4px; font-size: 0.8em; font-weight: bold; margin-left: 10px; }
  </style>
</head>
<body>
  <p><a href="../">← Back to Home</a> · <a href="../schema/">Schema</a></p>
  <h1>AVR Data Resources</h1>
  <div class="info-box">
    <p><strong>Data graph:</strong> <code>https://purl.humanatlas.io/graph/avr</code></p>
    <p><strong>Source data:</strong> <code>avr-data.source.json</code></p>
  </div>
  <div class="resource-grid">
    <div class="resource-card"><h3>Source JSON</h3><p>Downloaded AVR API payload.</p><a href="./avr-data.source.json">Open JSON</a></div>
    <div class="resource-card"><h3>LinkML YAML</h3><p>Normalized instance data.</p><a href="./avr-data.yaml">Open YAML</a></div>
    <div class="resource-card"><h3>LinkML JSON</h3><p>Canonical LinkML JSON export.</p><a href="./avr-data.json">Open JSON</a></div>
    <div class="resource-card"><h3>Turtle</h3><p>Primary RDF serialization.</p><a href="./avr-data.ttl">Open TTL</a></div>
  </div>
  <h2>Other Files</h2>
  <div id="data-files"><div class="file-list">Loading file list...</div></div>
  <script>
    const PRIMARY = new Set(["index.html","avr-data.source.json","avr-data.yaml","avr-data.json","avr-data.ttl","avr-data.jsonld","avr-data.owl","avr-data.nt","files.json"]);
    fetch('./files.json').then(r => r.ok ? r.json() : null).then(data => {
      const files = (data?.files || []).filter(file => !PRIMARY.has(file));
      if (!files.length) {
        document.getElementById('data-files').innerHTML = '<p>No additional files found.</p>';
        return;
      }
      const list = document.createElement('ul');
      list.className = 'file-list';
      files.sort((a,b) => a.localeCompare(b)).forEach(file => {
        const li = document.createElement('li');
        const link = document.createElement('a');
        link.href = './' + file;
        link.textContent = file;
        const badge = document.createElement('span');
        badge.className = 'file-type';
        badge.textContent = file.split('.').pop().toUpperCase();
        li.appendChild(link);
        li.appendChild(badge);
        list.appendChild(li);
      });
      document.getElementById('data-files').innerHTML = '';
      document.getElementById('data-files').appendChild(list);
    }).catch(() => {
      document.getElementById('data-files').innerHTML = '<p>Data manifest not available.</p>';
    });
  </script>
</body>
</html>
""",
    )


def write_schema_index_html(output_dir: Path) -> None:
    """Write the schema landing page."""
    _write_html(
        output_dir / "index.html",
        """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AVR Schema Resources</title>
  <style>
    body { max-width: 1000px; margin: 2rem auto; padding: 0 1rem; font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif; line-height: 1.6; color: #222; }
    a { color: #2f4fc2; }
    .info-box { background: #f0f4ff; border-left: 4px solid #667eea; padding: 20px; border-radius: 4px; margin-bottom: 20px; }
    .resource-grid { display: grid; grid-template-columns: repeat(auto-fit,minmax(220px,1fr)); gap: 16px; }
    .resource-card { border: 2px solid #eee; border-radius: 6px; padding: 16px; background: #fff; }
    .resource-card a { display: inline-block; text-decoration: none; color: white; background: #667eea; padding: 6px 12px; border-radius: 4px; font-weight: 500; }
    .file-list { list-style: none; background: #f5f5f5; padding: 20px; border-radius: 4px; border-left: 4px solid #667eea; }
    .file-list li { margin: 8px 0; padding: 8px; background: white; border-radius: 4px; display: flex; justify-content: space-between; align-items: center; }
    .file-type { display: inline-block; padding: 4px 8px; background: #667eea; color: white; border-radius: 4px; font-size: 0.8em; font-weight: bold; margin-left: 10px; }
  </style>
</head>
<body>
  <p><a href="../">← Back to Home</a> · <a href="../data/">Data</a> · <a href="./documentation/">Documentation</a></p>
  <h1>AVR Schema Resources</h1>
  <div class="info-box">
    <p><strong>Schema IRI:</strong> <code>https://purl.humanatlas.io/schema/avr</code></p>
    <p><strong>Property namespace:</strong> <code>https://purl.humanatlas.io/schema/avr#</code> (<code>avro:</code>)</p>
  </div>
  <div class="resource-grid">
    <div class="resource-card"><h3>LinkML Schema</h3><p>Canonical AVR LinkML schema source.</p><a href="./schema.yaml">Open YAML</a></div>
    <div class="resource-card"><h3>JSON Schema</h3><p>Validation schema for JSON-based integrations.</p><a href="./schema.json">Open JSON Schema</a></div>
    <div class="resource-card"><h3>JSON-LD Context</h3><p>Linked data context mapping for web clients.</p><a href="./schema.context.jsonld">Open Context</a></div>
    <div class="resource-card"><h3>OWL</h3><p>Ontology representation for semantic tooling.</p><a href="./schema.owl">Open OWL</a></div>
    <div class="resource-card"><h3>Mermaid ER Diagram</h3><p>Editable schema diagram source for docs and tooling.</p><a href="./schema.mmd">Open MMD</a></div>
    <div class="resource-card"><h3>SVG Diagram</h3><p>Rendered schema diagram in vector format.</p><a href="./schema.svg">Open SVG</a></div>
    <div class="resource-card"><h3>PNG Diagram</h3><p>Rendered schema diagram in raster format.</p><a href="./schema.png">Open PNG</a></div>
  </div>
  <h2>Other Files</h2>
  <div id="schema-files"><div class="file-list">Loading file list...</div></div>
  <script>
    const PRIMARY = new Set(["index.html","schema.yaml","schema.json","schema.context.jsonld","schema.owl","schema.mmd","schema.svg","schema.png","files.json"]);
    fetch('./files.json').then(r => r.ok ? r.json() : null).then(data => {
      const files = (data?.files || []).filter(file => !PRIMARY.has(file));
      if (!files.length) {
        document.getElementById('schema-files').innerHTML = '<p>No additional files found.</p>';
        return;
      }
      const list = document.createElement('ul');
      list.className = 'file-list';
      files.sort((a,b) => a.localeCompare(b)).forEach(file => {
        const li = document.createElement('li');
        const link = document.createElement('a');
        link.href = './' + file;
        link.textContent = file;
        const badge = document.createElement('span');
        badge.className = 'file-type';
        badge.textContent = file.split('.').pop().toUpperCase();
        li.appendChild(link);
        li.appendChild(badge);
        list.appendChild(li);
      });
      document.getElementById('schema-files').innerHTML = '';
      document.getElementById('schema-files').appendChild(list);
    }).catch(() => {
      document.getElementById('schema-files').innerHTML = '<p>Schema manifest not available.</p>';
    });
  </script>
</body>
</html>
""",
    )


def _markdown_to_html_page(markdown_text: str, title: str) -> str:
    md = MarkdownIt("commonmark", {"breaks": True, "html": True}).enable("table")
    rendered = md.render(markdown_text)
    rendered = re.sub(r'href="([^"]+)\.md(#.*?)?"', r'href="\1.html\2"', rendered)
    return (
        "<!DOCTYPE html>\n"
        '<html lang="en">\n'
        "<head>\n"
        '  <meta charset="UTF-8">\n'
        '  <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        f"  <title>{title}</title>\n"
        "  <style>\n"
        "    body { max-width: 1000px; margin: 2rem auto; padding: 0 1rem; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #222; }\n"
        "    a { color: #2f4fc2; }\n"
        "    table { border-collapse: collapse; width: 100%; margin: 1rem 0; }\n"
        "    th, td { border: 1px solid #ddd; padding: 0.5rem; text-align: left; vertical-align: top; }\n"
        "    th { background: #f4f6fb; }\n"
        "    code { background: #f4f4f4; padding: 0.1rem 0.3rem; border-radius: 4px; }\n"
        "    pre { background: #f7f7f7; padding: 1rem; overflow-x: auto; border-radius: 6px; }\n"
        "  </style>\n"
        "</head>\n"
        "<body>\n"
        f"{rendered}\n"
        "</body>\n"
        "</html>\n"
    )


def convert_markdown_directory_to_html(directory: Path) -> None:
    """Convert markdown docs in a directory to html and remove markdown files."""
    for md_path in sorted(directory.rglob("*.md")):
        markdown_text = md_path.read_text()
        title = md_path.stem
        first_line = markdown_text.splitlines()[0].strip() if markdown_text.splitlines() else ""
        if first_line.startswith("#"):
            title = first_line.lstrip("#").strip() or title
        html_path = md_path.with_suffix(".html")
        html_path.write_text(_markdown_to_html_page(markdown_text, title))
        md_path.unlink()


def _generate_mermaid_schema(schema_path: Path) -> str:
    """Generate a raw Mermaid ER diagram from the LinkML schema."""
    diagram = ERDiagramGenerator(str(schema_path), format="mermaid").serialize()
    if diagram.startswith("```mermaid"):
        diagram = diagram[len("```mermaid\n") :]
    if diagram.endswith("\n```"):
        diagram = diagram[:-len("\n```")]
    return diagram.strip() + "\n"


def _render_mermaid_to_images(mmd_path: Path, output_dir: Path) -> None:
    """Render a Mermaid diagram to SVG and PNG using the Mermaid CLI."""
    svg_path = output_dir / (mmd_path.stem + ".svg")
    png_path = output_dir / (mmd_path.stem + ".png")
    subprocess.run(
        [
            "npx",
            "-y",
            "@mermaid-js/mermaid-cli",
            "-q",
            "-i",
            str(mmd_path),
            "-o",
            str(svg_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        [
            "npx",
            "-y",
            "@mermaid-js/mermaid-cli",
            "-q",
            "-i",
            str(mmd_path),
            "-o",
            str(png_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def generate_schema_outputs(schema_path: Path, output_dir: Path) -> None:
    """Generate LinkML schema artifacts for publishing."""
    output_dir.mkdir(parents=True, exist_ok=True)
    documentation_dir = output_dir / "documentation"
    if documentation_dir.exists():
        shutil.rmtree(documentation_dir)
    documentation_dir.mkdir(parents=True, exist_ok=True)
    for legacy_markdown in output_dir.glob("*.md"):
        legacy_markdown.unlink()

    (output_dir / "schema.yaml").write_text(schema_path.read_text())
    (output_dir / "schema.json").write_text(JsonSchemaGenerator(str(schema_path)).serialize())
    (output_dir / "schema.context.jsonld").write_text(
        ContextGenerator(str(schema_path)).serialize()
    )
    (output_dir / "schema.owl").write_text(OwlSchemaGenerator(str(schema_path)).serialize())

    mermaid_source = _generate_mermaid_schema(schema_path)
    (output_dir / "schema.mmd").write_text(mermaid_source)
    _render_mermaid_to_images(output_dir / "schema.mmd", output_dir)

    (documentation_dir / "schema.erd.md").write_text(ERDiagramGenerator(str(schema_path)).serialize())
    (documentation_dir / "schema.erd.mmd").write_text(mermaid_source)
    _render_mermaid_to_images(documentation_dir / "schema.erd.mmd", documentation_dir)

    DocGenerator(str(schema_path), directory=str(documentation_dir)).serialize()
    convert_markdown_directory_to_html(documentation_dir)
    write_schema_index_html(output_dir)
