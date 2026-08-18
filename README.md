# epstein-docs-graph

An experiment in using a local LLM to extract people, organizations, and relationships from real documents and visualize them as an interactive graph.

**[View the live graph →](https://william3006.github.io/epstein-docs-graph/graph_epstein.html)**

## What this is

This project OCRs scanned document pages, sends the text to a local LLM (Qwen2.5, running via Ollama), and asks it to extract people and organizations mentioned, plus relationships between them, each backed by a direct quote from the source text. Results are merged, deduplicated (e.g. "Nixon" and "Richard Nixon" resolve to one entity), and rendered as an interactive force-directed graph — click any node to see its full connection history with quotes.

## How it works

Scanned page image → OCR (Tesseract) → raw text → LLM extraction (Qwen2.5 via Ollama) → structured JSON (entities + relations + quotes) → entity resolution (merge aliases) → filter unsupported claims (quote required) → graph_data.json → interactive D3.js graph.

Processing is checkpointed — if interrupted, it resumes from the last completed page rather than starting over.

## Important caveats

This is AI-extracted, not verified reporting. The LLM sometimes mislabels relationships, misses connections, or occasionally miscategorizes entities. Every edge is backed by a quote so you can check it against the source, but nothing here should be treated as a confirmed fact without checking that quote yourself. This is a personal, exploratory project, not a research publication or investigative product. It reflects a partial, small sample of a much larger public document release, not the full picture. Node size reflects how many connections an entity has in the processed sample, not their real-world significance.

## Tech stack

Python, Tesseract OCR, Ollama (Qwen2.5), NetworkX (prototyping), D3.js, rapidfuzz (entity resolution).

## Source documents

Documents processed here are drawn from the Epstein-related records release by the House Committee on Oversight and Government Reform, published September 2025.