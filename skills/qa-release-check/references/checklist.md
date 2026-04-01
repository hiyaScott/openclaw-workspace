# QA Release Checklist Reference

## Complete QA Checklist

### Web Page Deployment

| # | Check Item | Method | Pass Criteria |
|---|------------|--------|---------------|
| 1 | Page accessible | `curl -I URL` | HTTP 200 |
| 2 | No console errors | Browser DevTools | 0 errors |
| 3 | Responsive layout | Browser resize | Mobile + Desktop OK |
| 4 | All links work | Link checker | 0 broken links |

### Static Assets

| # | Check Item | Method | Pass Criteria |
|---|------------|--------|---------------|
| 1 | CSS loads | Network tab | HTTP 200, no 404 |
| 2 | JS loads | Network tab | HTTP 200, executes |
| 3 | Images display | Visual check | All images visible |
| 4 | Fonts load | Elements tab | Correct font family |

### Data Files (JSON/API)

| # | Check Item | Method | Pass Criteria |
|---|------------|--------|---------------|
| 1 | Valid JSON | `json.loads()` | No parse errors |
| 2 | Required fields | Schema check | All fields present |
| 3 | Data types correct | Type checking | String/Number/Array OK |
| 4 | References valid | URL check | All URLs accessible |

### GitHub Pages Specific

| # | Check Item | Method | Pass Criteria |
|---|------------|--------|---------------|
| 1 | Last-Modified updated | `curl -I` | Timestamp > deploy time |
| 2 | Cache invalidated | Hard refresh | New content visible |
| 3 | Custom domain works | DNS check | Domain resolves |

## Common Issues & Solutions

### Issue: CDN Cache Not Updated

**Symptom:** Last-Modified timestamp is old
**Solution:**
```bash
# Add cache-buster to URL
curl "https://example.com/data.json?t=$(date +%s)"
```

### Issue: Mixed Content (HTTP/HTTPS)

**Symptom:** Browser blocks resources
**Solution:** Use absolute HTTPS URLs

### Issue: CORS Errors

**Symptom:** API calls fail in browser
**Solution:** Check `_headers` or server CORS config

### Issue: Relative Path Resolution

**Symptom:** 404 on assets
**Solution:** Use absolute paths from domain root

## Report Templates

### Full Success Report

```markdown
## ✅ Deployment QA Report

**Project:** [name]
**Time:** [timestamp]
**URL:** [link]

### Summary
| Metric | Value |
|--------|-------|
| Checks Passed | X/Y |
| Duration | Xs |
| Status | ✅ PASS |

### Detailed Results

| Check | Status | Details |
|-------|--------|---------|
| Page HTTP | ✅ 200 | 45ms |
| JSON Valid | ✅ | 3 objects |
| Images | ✅ 7/7 | All 200 |
| Cache | ✅ | Updated |

### Notes
- [Any special notes]
- [Known limitations]
```

### Partial Success Report

```markdown
## ⚠️ Deployment QA Report

**Status:** PARTIAL (X/Y passed)

### Issues Found

| # | Issue | Severity | Action |
|---|-------|----------|--------|
| 1 | Image X 404 | Medium | Check path |
| 2 | Slow load | Low | Optimize later |

### Still Functional
- Core features working
- Main content visible

### Recommendation
Proceed with caveat: [specific warning]
```

### Failure Report

```markdown
## ❌ Deployment QA Report

**Status:** FAILED

### Critical Issues

| # | Issue | Impact | Fix |
|---|-------|--------|-----|
| 1 | Page 404 | High | Check branch |
| 2 | JSON parse error | High | Validate syntax |

### Required Actions
1. [ ] Fix issue 1
2. [ ] Re-run QA
3. [ ] Verify fix

### Do Not Proceed
Deployment not ready for use.
```
