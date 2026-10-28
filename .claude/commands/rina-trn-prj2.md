---
description: Rina Trn Prj2 - security-scan, publish index.html to a Claude artifact, update README, artifact page, validation workflow and artifact description
argument-hint: <claude-artifact-url>
allowed-tools: mcp__playwright__*, Read, Write, Edit, Glob, Grep, Bash(git:*), Bash(grep:*), Bash(ls:*), Bash(cat:*), Bash(python3:*), Artifact
---

Publish this project to the Claude artifact at: $ARGUMENTS

If `$ARGUMENTS` is empty or not a `https://claude.ai/artifact/<id>` link, stop and ask the user for the artifact link. Do not guess one and do not create a new artifact unless the user says so.

Work through the steps in order. Stop and report if any step fails; never skip the security scan. An artifact has no repo, no Actions and no About box, so steps 4 to 6 use the closest equivalents and say so in the final summary.

## 1. Security scan (before anything is published)

Scan `index.html` (and every file that will be published or committed) for:
- Secrets: API keys, tokens, passwords, private keys (`-----BEGIN`), `AKIA…`, `ghp_`/`github_pat_`, `sk-`, `xox[bp]-`, bearer tokens, connection strings.
- Sensitive files: `.env*`, `*.pem`, `*.key`, `id_rsa*`, credentials/config dumps.
- Personal data: real email addresses, phone numbers, internal hostnames or IPs.
- Project rule from CLAUDE.md: the real email address may appear only in `FORMSUBMIT_ENDPOINT`. A published artifact exposes that constant to every viewer, and viewers can see the page source, so if it holds a real address (anything other than `YOUR_EMAIL@example.com`), flag it and ask the user whether to proceed or publish with the placeholder.

Report findings as a short table (file, line, type) with secret values redacted. If anything is found, STOP and ask the user how to proceed. If clean, say so in one line and continue.

## 2. Read the artifact, then publish the code

1. Read the live artifact (`Artifact` action `read` on the link) so the publish builds on the current version.
2. Build the page file in the scratchpad directory, not in the repo, from `index.html`:
   - Remove the `<!DOCTYPE>`, `<html>`, `<head>`, `<body>` wrapper tags; the artifact service adds its own skeleton. Keep `<title>`, the `<style>` block, the body markup and the `<script>` block.
   - Keep the page theme-aware: every colour is a token on `:root`, dark values under `@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { … } }` and under `:root[data-theme="dark"]`, and `body` sets an explicit background from a token. Tokenize light-only literal colours in the scratchpad copy only.
   - Do not add storage APIs, external scripts, fonts or images (CLAUDE.md hard constraints).
3. Publish with the `Artifact` tool, passing the artifact link as `url` so the link stays the same. Omit `icon`.

## 3. README

Create or update `README.md`: project name, one-paragraph description, "Features" list, "Run locally" (open `index.html`, no build), "Live artifact" link (the artifact URL), "Notifications" (FormSubmit setup and one-time activation, and that the artifact viewer blocks the request so it shows the "email notification failed" warning there), and the "Demo mode, no persistence" note. Keep it accurate to `CLAUDE.md`. Edit in place; do not discard useful existing content.

### Screenshot (Playwright MCP)

Capture a fresh screenshot with the Playwright MCP tools (configured in `.mcp.json`) and embed it in the README:
1. `browser_navigate` to the local `index.html` (`file://<absolute path>/index.html`) and `browser_wait_for` the board to render (cards visible).
2. `browser_resize` to 1440x900, then `browser_take_screenshot` with type `png` and save it as `docs/screenshot.png`, overwriting the old one. Create `docs/` if missing.
3. Look at the image once to confirm the board, all four columns and the header are visible and nothing looks broken.
4. Make sure the README has `![<project name>](docs/screenshot.png)` directly under the title, adding or fixing it if not.
5. If the Playwright MCP tools are not available in this session, fall back to a headless Chromium script with the `playwright` Node package and say so in the final summary. If neither works, keep the old screenshot and tell the user.
The screenshot is a public image: the security scan also covers it, so only capture the seeded demo data and never enter real task data first.

## 4. Artifact page and its updates

Treat step 2 as the create/update of the artifact page. Make sure the page title is a short name ("ABC IT PMO Kanban Board", no explainer after a dash or colon) and that the one-sentence `description` passed on publish says what the board does. Re-run step 2 whenever `index.html` changes.

## 5. "CI/CD" for the artifact

Artifacts cannot be deployed by GitHub Actions, so use the nearest equivalent: create or update `.github/workflows/validate.yml` that runs on push and pull request and fails if `index.html` contains `localStorage`, `sessionStorage`, `indexedDB`, `document.cookie`, or an external `http(s)://` script, stylesheet or image (CLAUDE.md hard constraints), and warns if a real email address is found in `FORMSUBMIT_ENDPOINT`. It does not publish. Publishing stays a manual `/rina-trn-prj2 <artifact-link>` run. Keep the existing `deploy-pages.yml` untouched.

## 6. "About" section

The artifact's equivalent of an About box is its title and one-sentence `description`. Set them on the publish in step 2. If the repo has a GitHub Pages URL (`https://<owner>.github.io/<repo>/`), mention it in the README next to the artifact link and, only if the user asks, in the artifact description. Do not edit GitHub repo settings from this command.

## Finish: pie chart, executive summary and critical impact view (always)

Every run ends with all three of these, even when an earlier step failed or was skipped. Never omit them.

**1. Pie chart of all activities.** Count every task on the board by status (Backlog, In Progress, Blocked, Done). Read the tasks from the seed data in `index.html` (`seedTasks()`), because board state lives only in memory. Compute the counts with a short `python3` script, not by eye, and treat a task as overdue when its due date is before today and its status is not Done. Show the chart as a Mermaid pie block, then a plain-text table of the same numbers (counts and percentages) so it still reads where Mermaid does not render:

```mermaid
pie showData title All activities by status
    "Backlog" : <n>
    "In Progress" : <n>
    "Blocked" : <n>
    "Done" : <n>
```

Include only the four statuses and put the overdue count in one line under the chart.

**2. Executive summary: exactly 3 bullets, each actionable, ordered by impact to the company.** Keep it glanceable for management: each bullet is at most 20 words, starts with a bold figure taken from the pie chart (a percentage or count, for example `25% blocked (2):`), then a verb, the task ID and owner, and the next step. Put the summary to the right of the pie chart where the layout allows. Weigh them by the impact ranking in item 3, not by status alone. Do not name the same task in two bullets. Cover: (a) the highest-impact blocked or overdue work and who must unblock it, (b) the next highest-impact items and where the team should redirect effort (what to start, and what to pause), and (c) the single next action for the user, including anything they must do by hand, such as reconnecting GitHub. No generic advice, no more or fewer than three bullets.

**3. Critical impact view for management (always).** Rank every open (not Done) task by business impact to the company and flag the critical ones. Compute with the same script as the pie chart so the numbers are never guessed:
- Score = priority (Critical 40, High 25, Medium 10, Low 0) + 25 if overdue + 1 per day overdue (max 15) + 15 if Blocked + 10 for Compliance or Cybersecurity work (regulatory or security exposure). Done tasks score 0.
- A task is CRITICAL when it is not Done and is Critical priority or scores 60 or more.
- Show a separate section headed `🔴 CRITICAL: needs management attention (<count>)`, ranked highest impact first. Mark each item with the 🔴 critical icon and the word CRITICAL (never colour alone). For each item give: rank, ID, title, owner, due date, status, score, the reasons it scored (priority, days overdue, blocked, exposure) and one **Redirect** action: if Blocked, escalate the dependency to a sponsor and agree an unblock date; if in Backlog, move it to In Progress and name the lowest-impact open task to pause so capacity is redirected; if In Progress, protect the owner's time, agree a recovery date and add support.
- If nothing is critical, say "No critical items. Nothing needs redirection right now."
- Do not invent business impact beyond these inputs. If the user supplies other impact data (revenue, regulatory deadline, customer count), use it to adjust the ranking and say so.

Then list in a few lines: scan result, links published, files created or edited, and any step that used an equivalent or was skipped.
