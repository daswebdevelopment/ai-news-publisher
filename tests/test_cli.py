from pathlib import Path

from ai_news_publisher.cli import run


def test_cli_run_success_writes_digest(tmp_path: Path, capsys) -> None:
    input_path = tmp_path / "news.json"
    output_path = tmp_path / "digest.md"
    input_path.write_text(
        """
        [
          {
            "title": "Launch",
            "source": "Blog",
            "url": "https://example.com/launch",
            "summary": "Shipped",
            "published_at": "2026-01-02T10:00:00+00:00"
          }
        ]
        """,
        encoding="utf-8",
    )

    code = run([str(input_path), "--output", str(output_path)])

    assert code == 0
    assert output_path.exists()
    assert "Wrote 1 normalized stories" in capsys.readouterr().out


def test_cli_run_handles_missing_input_file(tmp_path: Path, capsys) -> None:
    missing_path = tmp_path / "missing.json"

    code = run([str(missing_path)])

    assert code == 1
    assert "Error reading input file" in capsys.readouterr().err


def test_cli_run_handles_invalid_json(tmp_path: Path, capsys) -> None:
    input_path = tmp_path / "bad.json"
    input_path.write_text("{bad json", encoding="utf-8")

    code = run([str(input_path)])

    assert code == 1
    assert "Error parsing JSON" in capsys.readouterr().err


def test_cli_run_handles_invalid_item_data(tmp_path: Path, capsys) -> None:
    input_path = tmp_path / "bad-item.json"
    input_path.write_text(
        """
        [
          {
            "title": "   ",
            "source": "Blog",
            "url": "https://example.com/launch",
            "summary": "Shipped",
            "published_at": "2026-01-02T10:00:00+00:00"
          }
        ]
        """,
        encoding="utf-8",
    )

    code = run([str(input_path)])

    assert code == 1
    assert "Invalid news item data" in capsys.readouterr().err
