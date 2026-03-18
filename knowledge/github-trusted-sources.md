# Trusted GitHub Sources

> **Purpose**: Whitelist of verified GitHub sources to mitigate security risks when referencing code.
> **Last Updated**: 2026-03-11

---

## Tier 1: Official Organizations (Safest)

These are official accounts of well-known companies and foundations:

| Organization | Verification | Notes |
|--------------|--------------|-------|
| `microsoft` | ✅ Official | Microsoft products and open source |
| `google` | ✅ Official | Google open source projects |
| `facebook` / `meta` | ✅ Official | Meta open source |
| `apache` | ✅ Official | Apache Software Foundation |
| `mozilla` | ✅ Official | Mozilla Foundation |
| `kubernetes` | ✅ Official | CNCF / Kubernetes project |
| `golang` | ✅ Official | Go programming language |
| `python` | ✅ Official | Python Software Foundation |
| `nodejs` | ✅ Official | Node.js project |
| `rust-lang` | ✅ Official | Rust programming language |
| `tensorflow` | ✅ Official | Google ML platform |
| `pytorch` | ✅ Official | Meta ML framework |

---

## Tier 2: Established Authors

Individual maintainers with proven track records:

| Author | Notable Projects | Verification |
|--------|------------------|--------------|
| *(Add as discovered)* | | |

---

## Tier 3: User-Vetted Projects

Specific projects manually approved for reference:

| Repository | Added Date | Approved By | Notes |
|------------|------------|-------------|-------|
| *(Add as approved)* | | | |

---

## Red Flags Checklist

When evaluating a new repository, check for these warning signs:

- [ ] Created very recently (< 6 months)
- [ ] High stars but few issues/PRs (bot-inflated)
- [ ] Name similar to popular project (typosquatting)
- [ ] Author has no other contributions (sock puppet)
- [ ] Dependencies include unknown/unverifiable packages
- [ ] README contains suspicious instructions or encoded data

---

## Usage Rules

1. **Tier 1**: Can reference with standard caution
2. **Tier 2**: Can reference, still review code before execution
3. **Tier 3**: User-approved, but still no direct execution
4. **Not on list**: Extra scrutiny required, flag to user before use
