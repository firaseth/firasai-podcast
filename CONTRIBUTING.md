# Contributing to FirasAi Podcast

Thanks for your interest in making this better. Contributions are welcome across all areas.

## What You Can Contribute

**Prompts** — Add or improve prompts in `02-Prompts-Library.md`. Include the use case, a clear prompt template, and an example output.

**Agent code** — Improve any file in `agent/`. Keep to the existing file-per-agent structure. Add error handling where missing.

**Automation blueprints** — Enhance `04-Make-Blueprints.md` with new Make.com or n8n flows. Include step-by-step screenshots or JSON exports where possible.

**Notion templates** — Expand `03-Notion-Template.md` with additional database views, formulas, or automations.

## How to Contribute

1. Fork the repo
2. Create a branch: `git checkout -b feature/my-improvement`
3. Make your changes
4. Commit with a clear message: `git commit -m "feat: add competitor analysis prompt"`
5. Open a pull request with a short description of what changed and why

## Code Style

- Python: follow PEP 8, use type hints, keep functions focused
- Markdown: use headers consistently, keep tables aligned
- No API keys or secrets in any file (use `.env.example` as the pattern)

## Questions?

Open an issue or reach out to [@firaseth](https://github.com/firaseth).
