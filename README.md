# transkun mcp

将 transkun（一个从 piano 到 midi）的模型，封装为 mcp。

## Installation

因为 uv 有个默认行为：

> In this case, PyTorch would be installed from PyPI, which hosts CPU-only wheels for Windows and macOS, and GPU-accelerated wheels on Linux (targeting CUDA 12.8, as of PyTorch 2.9.1):

```toml
[project]
name = "project"
version = "0.1.0"
requires-python = ">=3.14"
dependencies = [
  "torch>=2.9.1",
  "torchvision>=0.24.1",
]
```

[Using uv with PyTorch | uv](https://docs.astral.sh/uv/guides/integration/pytorch/#installing-pytorch)

同样一份 toml，Windows 和 MacOS 会拉取 CPU， linux 拉取 GPU。
我们的方案是采用 extra 作为条件控制。

所以，需要 `uv sync --extra torch-cuda128`

[pyproject.toml 参考](./pyproject.toml)

transkun 比较小，看了他的模型只有 不到那个 50MB。

## transkun 用法

transkun 在自己的 README 里面说，只要通过命令去调用就好了。
所以我们的 MCP 也是充当一个命令调用的工具。

```sh
# cpu call:
transkun input.mp3 output.mid
# gpu call:
transkun input.mp3 output.mid --device cuda
```

我们只需要加入 uv run 前缀就好，以 cuda 为例：

```sh
uv run transkun input.mp3 output.mid --device cuda
```

## 封装为 MCP

因为这个东西是一个命令行，而且没有进度条。
要么用 gradio，要么自己用 fast-mcp 搓一套。

采用 Gradio，用 Fast-MCP 那一套，获取自己本地的 uv 环境有点儿问题。
因为是从 `uv run MCP-server` 那边 call 的，所以环境是 MCP-server 一个单独的
要从这个单独的环境里面调用 Transkun 本身的环境，比较麻烦
关键是用 subprocess，在 kilo code agent 中实测会卡死。

如果在 Gradio 中调用，会有很多好处：

1. 开箱即用的 server，未来如果要 上云 会方便
2. 可视化界面调试
3. server 可以提供文件的上传和下载功能
4. Gradio 本身和 transkun 在同一个环境下，天然支持 `import torch`

tool name: `transcribe_piano_audio_to_midi_sync(audio_path, midi_path)`

sync 后缀表示同步的意思。synchronize
