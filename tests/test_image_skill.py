import json
from pathlib import Path
import subprocess
import sys

from PIL import Image


SCRIPT = Path(__file__).parents[1] / ".agents" / "skills" / "blogger-images" / "scripts" / "prepare_image.py"


def test_prepare_image_preserves_small_source_without_compression(tmp_path):
    source = tmp_path / "source.png"
    Image.new("RGB", (2000, 1000), "#336699").save(source)
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            str(source),
            "--output-dir",
            str(tmp_path / "output"),
            "--name",
            "ai-tool-workflow",
            "--alt",
            "AI 工具工作流程示意图",
            "--base-url",
            "https://xingcan-hu.github.io/blogger/images/2026/example",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)

    assert payload["width"] == 2000
    assert payload["height"] == 1000
    assert payload["output"].endswith("ai-tool-workflow.png")
    assert payload["markdown"].startswith("![AI 工具工作流程示意图](https://")
    output = tmp_path / "output" / "ai-tool-workflow.png"
    assert output.is_file()
    assert output.read_bytes() == source.read_bytes()
    assert payload["processing"] == "preserved_original"
    assert payload["output_bytes"] < 5_000_000


def test_prepare_image_optimizes_source_larger_than_two_mb(tmp_path):
    source = tmp_path / "large-source.bmp"
    Image.new("RGB", (2000, 1000), "#336699").save(source)
    assert source.stat().st_size > 2_000_000
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            str(source),
            "--output-dir",
            str(tmp_path / "output"),
            "--name",
            "large-source",
            "--alt",
            "大尺寸测试图片",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)

    assert payload["output"].endswith("large-source.webp")
    assert payload["processing"] == "optimized_webp"
    assert payload["output_bytes"] < 5_000_000


def test_prepare_image_rejects_unsafe_filename(tmp_path):
    source = tmp_path / "source.png"
    Image.new("RGB", (400, 300), "white").save(source)
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(source), "--output-dir", str(tmp_path), "--name", "Bad Name", "--alt", "说明"],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "lowercase ASCII" in result.stderr
