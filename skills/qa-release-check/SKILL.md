---
name: qa-release-check
description: Automated QA validation for web deployments. Use when deploying GitHub Pages, static sites, or web applications to automatically verify deployment success before notifying users. Triggers on deployment tasks, release confirmations, or when user requests QA validation.
---

# QA Release Check

Automated QA validation for web deployments. Ensures deployment success before notifying users.

## When to Use

- After deploying to GitHub Pages
- After updating static site content
- When user requests "/发布确认" or "QA check"
- Before saying "deployment complete" to user

## Standard QA Workflow

```
Deploy → Wait for sync → Run QA checks → Notify user
```

### Step 1: Run QA Checks

Use the provided script to validate deployment:

```bash
python3 /root/.openclaw/workspace/skills/qa-release-check/scripts/qa_check_pipeline.py
```

### Step 2: Interpret Results

**Exit 0 (Success):**
- All checks passed
- Safe to notify user "deployment complete"

**Exit 1 (Failure):**
- One or more checks failed
- Do NOT say "completed"
- Report specific failures and next steps

### Step 3: Report Format

**Success:**
```
✅ [Task] Deployment Successful

QA Check Results:
| Check Item | Status |
|------------|--------|
| Page accessible | ✅ HTTP 200 |
| JSON valid | ✅ |
| Images accessible | ✅ 7/7 |

URL: [link]
```

**Failure:**
```
❌ [Task] Deployment Issue

Problems:
- xxx check failed (HTTP 404)
- xxx data missing

Action Required: [specific next step]
```

## Pipeline QA Script

For AI Short Film Pipeline deployments, use:

```bash
python3 /root/.openclaw/workspace/skills/qa-release-check/scripts/qa_check_pipeline.py \
  --url https://hiyascott.github.io/hiyamax-blog \
  --project the_147th_day
```

Checks performed:
1. Page HTTP 200 status
2. JSON data validity
3. Video poster configurations
4. Poster image accessibility
5. Blueprint feature presence

## Extending for Other Projects

Copy and modify the script for new projects:

```python
# Create project-specific QA script
scripts/qa_check_[project].py
```

Key validation patterns:
- URL accessibility checks
- JSON schema validation
- Image/resource availability
- Content completeness

## Critical Rules

1. **Never say "completed" before QA**
2. **Always provide evidence** (HTTP codes, counts)
3. **Fail fast** - report issues immediately
4. **Suggest solutions** not just problems
