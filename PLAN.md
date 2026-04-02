# PLAN.md - Journaling Application Strategic Roadmap

## Vision

A **private, self-hosted journaling application** that grows with the user. The app should feel like a personal companion — not a social network. Every feature should reinforce three core principles:

1. **Privacy First** — All data stays on the user's machine. No telemetry, no cloud sync, no third-party analytics.
2. **AI as an Assistant, Not a Crutch** — AI enhances the experience (summaries, insights, Q&A) but the app is fully functional without it.
3. **Longevity** — Journals should be durable, exportable, and meaningful decades later.

---

## Current State

### Phase 0 — Foundation ✅
- Journal CRUD, Goals, Blurbs, AI features (toggleable), Authentication, Dark mode, 218 tests, `start.sh`

### Phase 1 — Usability & Discoverability ✅
- Dashboard, Search/Filter, Mood Calendar, Tags, Bookmarks, Export (JSON/MD), Streaks, Profile, Goal Progress, Weekly Report Command, Pagination, Navigation Bar

---

## Phase 2 — Intelligence & Reflection (Current Sprint)

**Goal:** Help users derive meaning from their journals over time. Move from "recording" to "understanding."

### Feature 1: Monthly Report Generation
**Problem:** Weekly reports exist but there's no monthly or longer-term perspective. Users can't see month-over-month patterns.
**Solution:** Extend the `generate_weekly_report` command to also generate monthly reports. Add a monthly report type to the Report model. Display monthly reports alongside weekly ones.

### Feature 2: "On This Day" / Memory Feature
**Problem:** Journals accumulate but past entries are forgotten. Users miss the joy of re-reading what they wrote on the same date in previous years.
**Solution:** A dashboard widget and dedicated page showing journal entries from the same date in previous years. "On this day in 2024, you wrote..."

### Feature 3: Mood Trend Chart
**Problem:** The mood calendar shows individual days but no trend over time. Users can't see if their mood is improving or declining.
**Solution:** A line chart (CSS/SVG-based, no JS libraries) showing mood frequency over weeks/months. Shows the top 3 moods per week as a stacked visualization.

### Feature 4: AI-Powered Goal Linking
**Problem:** The Goal model has a ManyToMany to JournalEntry but it's never populated. The README says AI should scan journals for goal references.
**Solution:** When a journal is submitted (and USE_AI=True), scan content for goal title/keyword matches and auto-link. When USE_AI=False, provide a manual "Link to Goal" selector on the journal form.

### Feature 5: Journal Entry Word Count & Stats
**Problem:** Users have no sense of their writing volume. No feedback on how much they're journaling.
**Solution:** Calculate and display word count, character count, and estimated reading time on each journal entry. Show total words written on the dashboard. Add a "writing stats" section.

### Feature 6: Journal Templates / Prompts
**Problem:** Users sometimes face blank-page syndrome. They don't know what to write about.
**Solution:** A set of built-in journal templates (e.g., "Daily Reflection", "Gratitude Journal", "Weekly Review", "Goal Check-in"). Users can start a journal from a template which pre-fills section headers.

### Feature 7: Journal Entry Drafts / Autosave
**Problem:** If a user starts writing and gets interrupted, their work is lost.
**Solution:** A Draft model that saves journal content periodically via a simple JavaScript autosave. Drafts are user-private and can be resumed or discarded.

### Feature 8: Annual Review Generation
**Problem:** At year-end, there's no way to reflect on the entire year.
**Solution:** A management command (`generate_annual_review`) that compiles a year-in-review: total entries, word count, top moods, most-used tags, goal progress summary, longest streak, and (with AI) a narrative summary.

### Feature 9: Journal Timeline View
**Problem:** The table view is functional but doesn't convey the narrative flow of a user's life.
**Solution:** A timeline visualization showing journal entries as a vertical timeline with dates, titles, mood badges, and truncated content. Clickable to expand. Filterable by tag and date range.

### Feature 10: Tag Edit, Merge, and Delete
**Problem:** Tags can accumulate duplicates or become messy. Users can't rename, merge, or delete tags.
**Solution:** Tag management page with rename, merge (move all entries from one tag to another), and delete (with confirmation) operations.

---

## Phase 3 — Polish & Scale (Future)

### Feature 11: Mobile-Responsive Templates
Ensure all pages work well on phones and tablets.

### Feature 12: Data Import
Import journals from other platforms (Day One, standard JSON, plain text files).

### Feature 13: Encryption at Rest
Optional database-level encryption for an extra layer of privacy.

### Feature 14: PWA Support
Make the app installable as a Progressive Web App for offline journaling.

### Feature 15: Journal Entry Search Within Content
Full-text search within a single journal entry to find specific passages.

---

## Technical Debt

- [ ] Extract magic strings (mood colors, goal length choices) into constants module
- [ ] Optimize `all_moods` query in journals view (currently iterates all entries)
- [ ] Add rate limiting for AI endpoints
- [ ] Consider switching from `CharField` to `TextField` for long content fields
- [ ] Add database indexes for frequently queried fields
- [ ] Consolidate dark-mode cookie scripts into a single include

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Test coverage | >85% |
| All features work with USE_AI=False | Yes |
| Zero external dependencies (non-AI mode) | Yes |
| Export includes all user data | Yes |
| Setup time for new user | <2 minutes |
