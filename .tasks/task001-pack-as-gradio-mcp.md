# 实现 local_mcp

将 transkun 命令行封装为一个 MCP 调用。
对外暴露的 tool 叫做 `transcribe_piano_audio_to_midi_sync(audio_path, midi_path)`
都是 locally path，并且在 docstring 中要告知使用 absolute local path

用 Gradio 对外暴露，每次 tool call 的时候，需要判断本地有没有 cuda 环境。
这个 MCP 本身就和 transkun 安装在了一起。

```sh
# cpu call:
uv run transkun input.mp3 output.mid
# gpu call:
uv run transkun input.mp3 output.mid --device cuda
```
