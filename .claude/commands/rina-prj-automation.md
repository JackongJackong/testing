---
description: Rina Prj Automation - security-scan, push to a GitHub repo, update README, Pages, CI/CD workflow and the repo About section
argument-hint: <github-repo-url>
allowed-tools: mcp__playwright__*, Bash(git:*), Bash(python3:*), Bash(grep:*), Bash(ls:*), Bash(cat:*), Read, Write, Edit, Glob, Grep, mcp__github__*
---

Publish this project to the GitHub repository at: $ARGUMENTS

If `$ARGUMENTS` is empty or not a `https://github.com/<owner>/<repo>` URL, stop and ask the user for the repo link. Do not guess one.

Work through the steps in order. Stop and report if any step fails; never skip the security scan and never force-push.

## 1. Security scan (before anything leaves this machine)

Scan every file that would be committed (`git ls-files` plus untracked, non-ignored files) and the full git history that will be pushed (`git log -p`) for:
- Secrets: API keys, tokens, passwords, private keys (`-----BEGIN`), `AKIA…`, `ghp_`/`github_pat_`, `sk-`, `xox[bp]-`, bearer tokens, connection strings.
- Sensitive files: `.env*`, `*.pem`, `*.key`, `id_rsa*`, credentials/config dumps.
- Personal data: real email addresses, phone numbers, internal hostnames or IPs.
- Project rule from CLAUDE.md: the real email address must appear only in `FORMSUBMIT_ENDPOINT`. A public repo and public Pages site expose that constant in plain text, so if it holds a real address (anything other than `YOUR_EMAIL@example.com`), flag it and ask the user whether to proceed or use a placeholder.

Report findings as a short table (file, line, type). Redact the secret value in the report. If anything is found, STOP and ask the user how to proceed. If clean, say so in one line and continue.

## 2. Push the code

1. Show `git remote -v`. If no remote points at the given URL, add it as `origin` only if `origin` does not exist; otherwise add it as `publish` and tell the user. Never remove or rewrite existing remotes.
2. Make sure everything is committed (ask before committing unrelated changes).
3. Push the current branch: `git push -u <remote> <branch>`. Retry network failures up to 4 times (2s, 4s, 8s, 16s). A 403 is an auth problem, not a network one: report it and point the user to https://claude.ai/connect-github instead of retrying.
4. GitHub Pages deploys from the default branch (`master` in `.github/workflows/deploy-pages.yml`). If the work is on another branch, ask the user before merging or opening a PR.

## 3. README

Create or update `README.md`: project name, one-paragraph description, a screenshot-free "Features" list, "Run locally" (open `index.html`, no build), "Live demo" link (filled in at step 5), "Notifications" (FormSubmit setup and one-time activation), and the "Demo mode, no persistence" note. Keep it accurate to `CLAUDE.md`. Edit in place if a README exists; do not discard useful existing content.

### Screenshot (Playwright MCP)

Capture a fresh screenshot with the Playwright MCP tools (configured in `.mcp.json`) and embed it in the README:
1. `browser_navigate` to the local `index.html` (`file://<absolute path>/index.html`) and `browser_wait_for` the board to render (cards visible).
2. `browser_resize` to 1440x900, then `browser_take_screenshot` with type `png` and save it as `docs/screenshot.png`, overwriting the old one. Create `docs/` if missing.
3. Look at the image once to confirm the board, all four columns and the header are visible and nothing looks broken.
4. Make sure the README has `![<project name>](docs/screenshot.png)` directly under the title, adding or fixing it if not.
5. If the Playwright MCP tools are not available in this session, fall back to a headless Chromium script with the `playwright` Node package and say so in the final summary. If neither works, keep the old screenshot and tell the user.
The screenshot is a public image: the security scan also covers it, so only capture the seeded demo data and never enter real task data first.

Steps 3 to 7 change files after the step 2 push, so commit them and push again before finishing (same rules as step 2).

## 4. CI/CD workflow

Create or update `.github/workflows/deploy-pages.yml`: trigger on push to the default branch and `workflow_dispatch`; permissions `contents: read`, `pages: write`, `id-token: write`; build the `_site/` folder by copying `index.html`; deploy with `actions/configure-pages`, `actions/upload-pages-artifact`, `actions/deploy-pages`. Keep the existing file if it already does this. Optionally add a lightweight job that fails the build if `index.html` contains `localStorage`, `sessionStorage`, `indexedDB`, `document.cookie`, or an external `http(s)://` script/stylesheet (CLAUDE.md hard constraints).

## 5. GitHub Pages

Use the GitHub tools to enable Pages with source "GitHub Actions" if it is not already enabled, then trigger or wait for the deploy workflow. The site URL is `https://<owner>.github.io/<repo>/`. Verify the workflow run succeeded before reporting the URL. If Pages cannot be enabled with the available tools, tell the user to do it at Settings > Pages > Source: GitHub Actions.

## 6. Repo About section

Set the repo description to a short summary of the project and add topics (for example `kanban`, `vanilla-js`, `html`, `demo`). Use the GitHub tools; if they cannot edit repo metadata, give the user the exact text to paste.

## 7. Add the Pages link to About

Set the repo homepage/website field to the Pages URL from step 5, and put the same link in the README "Live demo" section.

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
