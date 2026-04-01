# TODO.md - Journaling Application Tasks

## Overview
Tasks identified from reviewing the README.md and codebase for the Django Journaling Application.

---

## Phase 0 — Foundation (Completed)

| Task | Status |
|------|--------|
| Fix `created_at` fields (`auto_now` → `auto_now_add`) | ✅ Done |
| Add logout view and URL route | ✅ Done |
| Make Ollama API URL configurable via env vars | ✅ Done |
| Add `USE_AI` environment variable (default: False) | ✅ Done |
| Fix goal list ordering | ✅ Done |
| Add goal edit/delete functionality | ✅ Done |
| Add journal edit/delete functionality | ✅ Done |
| Add local development setup instructions to README | ✅ Done |
| Add `start.sh` one-command setup script | ✅ Done |

## Phase 1 — Usability & Discoverability (Completed)

| Feature | Status | Tests |
|---------|--------|-------|
| **1. Dashboard** — Stats, streaks, recent entries, quick actions | ✅ Done | 10 |
| **2. Journal Search & Filtering** — Text search, mood/date/tag filters | ✅ Done | 11 |
| **3. Mood Calendar** — Heatmap visualization, clickable cells | ✅ Done | 8 |
| **4. Tags System** — Tag model, ManyToMany, CRUD views | ✅ Done | 14 |
| **5. Bookmarks** — Toggle, display on dashboard/detail | ✅ Done | 6 |
| **6. Export Journals** — JSON and Markdown download | ✅ Done | 10 |
| **7. Streak Detail Page** — All streaks, current/longest stats | ✅ Done | 9 |
| **8. Profile Management** — Profile page, password change | ✅ Done | 14 |
| **9. Goal Progress Tracking** — 0-100% field, progress bar | ✅ Done | 15 |
| **10. Weekly Report Command** — `generate_weekly_report` management command | ✅ Done | 8 |
| **Pagination** — All listing views paginated | ✅ Done | 12 |
| **Navigation Bar** — Consistent nav across all pages | ✅ Done | 12 |
| **Code Polish** — Removed debug prints, updated testing.md | ✅ Done | 1 |

## Phase 2 — Intelligence & Insights (Future)

| Feature | Priority | Status |
|---------|----------|--------|
| AI-Powered Goal Linking | Low | 📋 Planned |
| Daily Suggestions/Feedback | Low | 📋 Planned |
| Trend Analysis | Low | 📋 Planned |
| Sentiment Over Time Graph | Low | 📋 Planned |
| Annual Review | Low | 📋 Planned |

## Phase 3 — Polish & Scale (Future)

| Feature | Priority | Status |
|---------|----------|--------|
| Mobile-Responsive Templates | Medium | 📋 Planned |
| Data Import (Day One, JSON, text) | Low | 📋 Planned |
| Encryption at Rest | Low | 📋 Planned |
| PWA Support | Low | 📋 Planned |

---

## Test Summary

| Metric | Value |
|--------|-------|
| Total Tests | 218 |
| Passing | 218 |
| Failing | 0 |
| Test Classes | 32 |
| Last Run | 2026-04-01 |

## Technical Debt

- [ ] Extract magic strings (mood colors, goal length choices) into constants module
- [ ] Add rate limiting for AI endpoints
- [ ] Consider switching from `CharField` to `TextField` for long content fields
- [ ] Optimize `all_moods` query in journals view (currently iterates all entries)

## Commit History (Phase 1)

| Commit | Description |
|--------|-------------|
| 055aac0 | Add remaining Phase 1 files: goal progress model/migration, password change templates, PLAN.md |
| 282f55e | Features 9-10: Weekly report management command, pagination, nav bar, and polish |
| 7caa349 | Implement Phase 1 Features 1-4: Dashboard, Search/Filter, Mood Calendar, Tags |
| 9f2166e | Add USE_AI environment variable to disable AI features |
| bf5d410 | Add tests for USE_AI disabled mode and JournalForm conditional fields |
| 84e602c | Add goal and journal edit/delete functionality with tests and updated README |
| 4eec386 | Fix created_at fields, add Ollama config, logout view, and goal ordering |
