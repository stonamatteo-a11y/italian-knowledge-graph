import json

from ikg.cli import main


def test_review_command_returns_success_with_suggestions(tmp_path, capsys) -> None:
    graph = tmp_path / "graph.json"
    graph.write_text(
        json.dumps(
            {
                "entities": [
                    {"id": "m1", "type": "Macroarea", "label": "Scienze"},
                    {"id": "a1", "type": "Area", "label": "Fisica", "parent": "m1"},
                    {"id": "s1", "type": "Sottoarea", "label": "Meccanica", "parent": "a1"},
                    {"id": "c1", "type": "Concetto", "label": "X", "parent": "s1"},
                ]
            }
        ),
        encoding="utf-8",
    )

    result = main(["review", str(graph)])

    output = capsys.readouterr().out
    assert result == 0
    assert "Review suggestions: 2" in output
    assert "Entity c1" in output
    assert "Label is unusually short" in output


def test_review_command_fails_only_for_validation_errors(tmp_path, capsys) -> None:
    graph = tmp_path / "invalid.json"
    graph.write_text(
        json.dumps({"entities": [{"id": "a1", "type": "Area", "label": "Fisica"}]}),
        encoding="utf-8",
    )

    result = main(["review", str(graph)])

    output = capsys.readouterr().out
    assert result == 1
    assert "IKG200 ERROR" in output
    assert "Review suggestions:" not in output
