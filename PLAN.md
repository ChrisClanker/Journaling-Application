# PLAN.md - Journaling Application Strategic Roadmap

## Vision

A **private, self-hosted journaling application** that grows with the user. The app should feel like a personal companion — not a social network. Every feature should reinforce three core principles:

1. **Privacy First** — All data stays on the user's machine. No telemetry, no cloud sync, no third-party analytics.
2. **AI as an Assistant, Not a Crutch** — AI enhances the experience (summaries, insights, Q&A) but the app is fully functional without it.
3. **Longevity** — Journals should be durable, exportable, and meaningful decades later.

---

## Current State (Phase 0 — Foundation)

The app has a solid foundation:
- ✅ Journal CRUD (create, read, update, delete)
- ✅ Goals journal with hierarchy and expiration
- ✅ Blurbs (Signal integration for quick thoughts)
- ✅ AI-powered features (title generation, mood extraction, journal Q&A, weekly summaries)
- ✅ AI toggle (`USE_AI=False` by default — fully functional without AI)
- ✅ Authentication and logout
- ✅ Dark mode
- ✅ 71 passing tests
- ✅ One-command local setup (`start.sh`)

---

## Phase 1 — Usability & Discoverability (Current Sprint)

**Goal:** Make the app feel polished and help users get value from their existing data.

### Feature 1: Dashboard Home Page
**Problem:** The journal index is just a table. Users land on it and see a wall of text with no sense of their journaling habits.
**Solution:** A dashboard with key stats (total entries, current streak, mood distribution), recent entries, and quick actions. Shows users their journey at a glance.

### Feature 2: Journal Search & Filtering
**Problem:** As journals accumulate, finding a specific entry becomes impossible.
**Solution:** Full-text search across journal content, title, reflections, and gratitude fields. Filter by date range, mood, and tags.

### Feature 3: Mood Calendar Visualization
**Problem:** Mood data exists but is buried in individual entries. Users can't see patterns.
**Solution:** A calendar heatmap (like GitHub contributions) showing mood colors per day. Click a day to jump to that entry.

### Feature 4: Journal Tags/Topics System
**Problem:** Journals have no categorization beyond mood. Users can't organize by theme.
**Solution:** A Tag model with ManyToMany to JournalEntry. Users can create tags like "work", "family", "health" and filter by them.

### Feature 5: Export Journals (JSON/Markdown)
**Problem:** The "longevity" promise is empty if data is locked in the database.
**Solution:** Export all journals as a downloadable JSON file or formatted Markdown document. One-click backup.

### Feature 6: Streak Tracking
**Problem:** No gamification or habit reinforcement. Users don't know their consistency.
**Solution:** Calculate and display current streak, longest streak, and total journaling days on the dashboard.

### Feature 7: Password Change & Profile Management
**Problem:** Users can't change their password or manage their profile from within the app.
**Solution:** Profile page with password change form and username display.

### Feature 8: Goal Progress Tracking
**Problem:** Goals have a deadline but no way to track progress toward them.
**Solution:** Add a `progress` field (0-100%) to goals. Display a progress bar on goal detail. Allow manual progress updates.

### Feature 9: Bookmark/Favorite Journal Entries
**Problem:** Users can't mark important entries for quick return.
**Solution:** Add a `bookmarked` boolean field to JournalEntry. Show bookmarks on the dashboard and in a dedicated bookmarks page.

### Feature 10: Weekly Report Generation Management Command
**Problem:** Weekly summaries exist in the model but there's no way to generate them on demand or via cron.
**Solution:** A Django management command (`generate_weekly_report`) that can be run manually or scheduled via cron. Works with or without AI.

---

## Phase 2 — Intelligence & Insights (Future)

### Feature 11: AI-Powered Goal Linking
When a journal is submitted, AI scans it for references to active goals and auto-links them.

### Feature 12: Daily Suggestions/Feedback
After journaling, AI provides one actionable suggestion for the next day based on journal content.

### Feature 13: Trend Analysis
Track topics over time. Show which themes are growing, fading, or stable in the user's life.

### Feature 14: Sentiment Over Time Graph
Plot mood/sentiment scores on a timeline graph to visualize emotional patterns.

### Feature 15: Annual Review
At year-end, generate a comprehensive review: top moods, most common topics, goal progress, and key moments.

---

## Phase 3 — Polish & Scale (Long-Term)

### Feature 16: Multi-User Support
Support multiple users on the same instance with proper data isolation (already partially done via ForeignKey).

### Feature 17: Mobile-Responsive Templates
Ensure all pages work well on phones and tablets.

### Feature 18: Data Import
Import journals from other platforms (Day One, standard JSON, plain text files).

### Feature 19: Encryption at Rest
Optional database-level encryption for an extra layer of privacy.

### Feature 20: PWA Support
Make the app installable as a Progressive Web App for offline journaling.

---

## Technical Debt to Address

- [ ] Remove debug `print()` statements from views.py
- [ ] Extract magic strings (mood colors, goal length choices) into constants
- [ ] Add pagination to journal and goal listing views
- [ ] Add CSRF token validation testing
- [ ] Add rate limiting for AI endpoints
- [ ] Consider switching from `CharField` to `TextField` for long content fields

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Test coverage | >85% |
| All features work with USE_AI=False | Yes |
| Zero external dependencies (non-AI mode) | Yes |
| Export includes all user data | Yes |
| Setup time for new user | <2 minutes |
