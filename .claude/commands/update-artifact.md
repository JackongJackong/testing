---
description: Republish index.html to the existing Claude artifact (no GitHub needed)
argument-hint: [artifact-url]
allowed-tools: Read, Write, Edit, Bash(grep:*), Bash(sed:*), Bash(python3:*), Artifact
---

Republish the current `index.html` to the Claude artifact. Use `$ARGUMENTS` as the artifact URL if given, otherwise `https://claude.ai/artifact/NXNf7FCCXpLvF4QHNC4m9t`.

1. Read the live artifact first (`Artifact` action `read` on the URL) so the publish builds on the current version.
2. Build the page file in the scratchpad directory, not in the repo, from `index.html`:
   - Remove the `<!DOCTYPE>`, `<html>`, `<head>`, `<body>` wrapper tags; the artifact service adds its own skeleton. Keep `<title>`, the `<style>` block, the body markup and the `<script>` block.
   - Keep the page theme-aware: every colour is a token on `:root`, with dark values under `@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { … } }` and under `:root[data-theme="dark"]`, and `body` sets an explicit background from a token. If `index.html` has literal colours that only work in light mode, tokenize them in the scratchpad copy only; do not change `index.html` for this.
   - Do not add storage APIs, external scripts, fonts or images (CLAUDE.md hard constraints).
3. Publish with the `Artifact` tool using the same URL (`url` parameter) so the link stays the same. Omit `icon`.
4. Report the URL and one line on what changed. Mention that the artifact viewer blocks the FormSubmit request, so adding a task shows the "email notification failed" warning there; the board itself is unaffected.
