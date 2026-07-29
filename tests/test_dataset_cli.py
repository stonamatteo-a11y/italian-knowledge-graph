import json

import pytest

from ikg.cli import main


@pytest.mark.parametrize("format_name", ("jsonl", "csv"))
def test_cli_exports_dataset(tmp_path, format_name: str) -> None:
    graph = tmp_path / "graph.json"
    output = tmp_path / f"dataset.{format_name}"
    graph.write_text(
        json.dumps(
            {
                "entities": [
                    {"id": "m1", "type": "Macroarea", "label": "Scienze"},
                    {"id": "a1", "type": "Area", "label": "Fisica", "parent": "m1"},
                ],
                "relationships": [{"id": "r1", "type": "CONTAINS", "source": "m1", "target": "a1"}],
            }
        ),
        encoding="utf-8",
    )

    result = main(
        [
            "export",
            "dataset",
            "--input",
            str(graph),
            "--format",
            format_name,
            "--output",
            str(output),
        ]
    )

    assert result == 0
    assert output.is_file()
