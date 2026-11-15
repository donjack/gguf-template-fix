---
license: apache-2.0
base_model: dahara1/Qwen3.5-4B-UD-japanese-imatrix
language:
  - ja
  - en
tags:
  - gguf
  - qwen3.5
  - chat-template-fix
  - llama-cpp
  - pocketpal
---

# Qwen3.5-4B-UD-Q4_K_XL — embedded chat template fixed

This repository is a **drop-in replacement** for the GGUF file in
[dahara1/Qwen3.5-4B-UD-japanese-imatrix](https://huggingface.co/dahara1/Qwen3.5-4B-UD-japanese-imatrix).
The model weights are **completely unchanged**. The only modification is the
chat template embedded in the GGUF metadata, replaced with dahara1's own
standalone `chat_template.jinja` — the version he fixed on 2026-04-09.

## What was wrong, and what changed

Qwen3.5's stock chat template emits an empty `<think>` block for historical
assistant turns that have no reasoning content. This makes the rendered prompt
differ from what was processed before, so prefix caching breaks and multi-turn
or tool-use conversations get reprocessed from scratch (slower responses, more
heat) — see the original report on
[r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/comments/1sg076h/i_tracked_a_major_cache_reuse_issue_down_to_qwen/).
Output correctness is not affected.

dahara1 fixed this in his standalone `chat_template.jinja` (update dated
2026-04-09 in his repository) by adding one guard condition:

```diff
- {%- if loop.index0 > ns.last_query_index %}
+ {%- if loop.index0 > ns.last_query_index and reasoning_content %}
```

However, the template **embedded inside the GGUF file** still carries the
unfixed line, and runtimes such as llama.cpp and PocketPal use the embedded
template. This repository applies dahara1's own fix to the embedded copy.

## Verification

- Source file: `Qwen3.5-4B-UD-Q4_K_XL.gguf` from the base repository,
  sha256 `e57e3a553c1e90e1d320980fe5a8312650a6f3d9b9dc7764377d80b19192f097`
  (matches the hash published by Hugging Face for the source file).
- The embedded template was extracted from the source GGUF and diffed against
  the standalone `chat_template.jinja`: exactly one line differed (the guard
  above).
- The rewrite was done with `gguf-new-metadata` from llama.cpp's official
  gguf-py tools (`--chat-template-file`), which rewrites metadata only.
  Tensor data is copied verbatim.
- After the rewrite, the embedded template was re-extracted and confirmed to
  contain `ns.last_query_index and reasoning_content`.

## Usage

Use exactly like the original file — same filename, same settings.
In PocketPal, add this repository and download the GGUF from it instead of
the base repository. In llama.cpp you can alternatively keep the original
file and pass `--chat-template-file chat_template.jinja`.

## Notes

- Unofficial republish for a metadata-only fix; not affiliated with dahara1.
  For anything about the model itself (quality, quantization, benchmarks),
  please refer to the [base repository](https://huggingface.co/dahara1/Qwen3.5-4B-UD-japanese-imatrix).
- 日本語：本リポジトリは dahara1 氏の GGUF について、埋め込みチャットテンプレートだけを
  氏自身が配布している修正済み jinja に差し替えたものです。重みは一切変更していません。
  複数ターン会話でのキャッシュ再利用（速度・発熱）に関する修正であり、出力の内容は変わりません。

## 謝辞 / Acknowledgments

- [dahara1](https://huggingface.co/dahara1) — the base GGUF, the Japanese
  imatrix UD quantization, and the fixed standalone chat template this
  repository embeds.
- [Qwen](https://huggingface.co/Qwen/Qwen3.5-4B) — the original model.
- [llama.cpp / gguf-py](https://github.com/ggml-org/llama.cpp) — the
  `gguf-new-metadata` tool used for the rewrite.
- The r/LocalLLaMA reporter who tracked down the cache-reuse issue.
- Thank you to all AI researchers and practitioners.
