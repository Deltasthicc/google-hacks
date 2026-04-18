# Submission Checklist

Tracks the artifacts the Solution Challenge 2026 India submission needs. Current deadline for prototype submission: 24 April 2026.

## Required submission artifacts

- [ ] **Problem statement** finalized → `docs/submission/problem_statement.md`
- [ ] **Solution overview** finalized → `docs/submission/solution_overview.md`
- [ ] **MVP live link** ready and reachable without sign-in required beyond a demo Google account
- [ ] **Public GitHub repository** with a clean README and working setup instructions
- [ ] **Project deck** (Google Slides or PDF) following `docs/pitch/deck_outline.md`
- [ ] **Demo video** (3 to 5 minutes) following `docs/pitch/demo_script.md`
- [ ] **Individual registrations** completed by every team member on the challenge portal
- [ ] **Team formation** completed on the challenge portal, one submission per team

## Narrative readiness

- [ ] Team can deliver the one-line pitch from `solution_overview.md` without notes
- [ ] Team can explain the Iqbal & Ismail grounding in under sixty seconds
- [ ] Team has a clear answer to "what makes this different from AIF360?"
- [ ] Team has a clear answer to "how is this safe if the AI writes the report?"
- [ ] Team has a clear answer to "which SDG does this address?" (SDG 10 primary, 16 and 5 secondary)

## Product readiness

- [ ] Lending demo pack (South German Credit) runs end-to-end in the live MVP
- [ ] Hiring demo pack (Adult) runs end-to-end in the live MVP
- [ ] At least one policy PDF walkthrough runs end-to-end and produces a policy-alignment block in the report
- [ ] BigQuery audit history populates and the Looker dashboard loads without errors
- [ ] Export to Markdown, HTML, and JSON all work from the UI

## Technical readiness

- [ ] `python -c "from app.ai_reports import generate_report"` succeeds against a live Gemini key
- [ ] `backend/app/tests/test_reports.py` passes
- [ ] Backend deploys cleanly to Cloud Run
- [ ] Firebase Hosting for the Flutter web app deploys cleanly
- [ ] Firestore and Storage security rules are at least restrictive enough to pass a basic review (no world-readable buckets, no unauthenticated writes)
- [ ] App Check is enabled on the Firebase project to protect the Gemini calls

## Content assets

- [ ] At least five screenshots captured for the deck and README: sign-in, upload, audit running, report view (executive), report view (technical), Looker dashboard
- [ ] Demo video has a title card, a voiceover that matches `demo_script.md`, and a closing frame with the team name and links
- [ ] README has a working "Try it" section pointing to the live MVP

## Cosmetic polish

- [ ] Repository has a `LICENSE`, `CODE_OF_CONDUCT.md`, and `CONTRIBUTING.md`
- [ ] No secrets committed to the repo (verified with `git log -p | grep -Ei 'api[_-]?key|secret'`)
- [ ] `.env.example` present, `.env` not present
- [ ] Architecture diagram in the deck matches `ARCHITECTURE.md`

## Submission-day logistics

- [ ] Submission form filled on the challenge portal at least 12 hours before the deadline
- [ ] Demo video uploaded as unlisted YouTube or Google Drive link (not publicly shared, but not requiring sign-in to view)
- [ ] Backup of the repo zipped and stored in a shared team Drive in case of GitHub issues
- [ ] One teammate assigned as submission lead and reachable on the day
