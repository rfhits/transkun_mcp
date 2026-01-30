"""Minimal Gradio front-end that wraps inference.py via subprocess."""

from __future__ import annotations

import json
import shlex
import subprocess
import sys
import time
from pathlib import Path
from typing import Iterable, Iterator, List

import gradio as gr

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _detect_device() -> str:
    try:
        import torch

        if torch.cuda.is_available():
            return "cuda"
    except ImportError:
        return "cpu"


device = _detect_device()


def build_command(
    audio_path: str,
    midi_path: str,
) -> List[str]:
    """Construct the CLI command used to launch transkun"""

    cmd: List[str] = ["uv", "run", "transkun", audio_path, midi_path]
    if device == "cuda":
        cmd.extend(["--device", "cuda"])

    return cmd


def transcribe_piano_audio_to_midi_sync(audio_path: str, midi_path: str) -> str:
    """transcribe piano audio to midi sync.

    Args:
        audio_path: audio path, use full path.
        midi_path : midi path, use full path.

    Returns:
        str: The combined stdout and stderr from the subprocess.
    """
    cmd = build_command(
        audio_path=audio_path,
        midi_path=midi_path,
    )
    quoted_cmd = " ".join(shlex.quote(part) for part in cmd)
    try:
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as exc:
        return f"Failed to run inference script: {exc}\nCommand: {quoted_cmd}"
    output_sections = [
        f"$ {quoted_cmd}",
        "",
        completed.stdout.strip(),
        completed.stderr.strip(),
    ]
    return "\n".join(section for section in output_sections if section)


demo = gr.Interface(
    fn=transcribe_piano_audio_to_midi_sync,
    inputs=[gr.Textbox(), gr.Textbox()],
    outputs=[gr.Textbox()],
    title="transcribe_piano_audio_to_midi CLI Wrapper",
    description="transcribe piano audio to MIDI using transkun via CLI.",
    api_name="transcribe_piano_audio_to_midi_sync",
)


def main() -> None:
    _, local_url, share_url = demo.launch(mcp_server=True, prevent_thread_lock=True)

    # 动态获取最终 URL
    target_url = share_url if share_url else local_url
    mcp_endpoint = f"{target_url.rstrip('/')}/gradio_api/mcp/"

    config = {
        "transkun": {
            "command": "npx",
            "args": ["mcp-remote", mcp_endpoint],
        }
    }

    print("\n" + "🚀" * 10)
    print("复制以下配置到你的 MCP 客户端：")
    print(json.dumps(config, indent=2))
    print("🚀" * 10 + "\n")

    # 因为设置了不阻塞，如果不加这个死循环，脚本执行完打印就直接退出了
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        demo.close()


if __name__ == "__main__":
    main()
