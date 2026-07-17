# Release & Archive Workflow

When user says "archive tasks and create a milstore and make a version and push everything and make release using gh":

1. **Load skills**: `archive-tasks`, `versioning-and-release`
2. **Archive completed tasks**:
   - Read all tasks in `tasks/completed/`
   - Read highest existing milestone number from `docs/history/milestone-N-summary.md`
   - Create `docs/history/milestone-N+1-summary.md` with condensed summaries
   - `mv tasks/completed/*.md tasks/archive/`
3. **Bump version**:
   - Read current `<system_version>` from `system-prompt.md`
   - Determine bump type: PATCH for docs/fixes, MINOR for features, MAJOR for breaking
   - Update `<system_version>` in `system-prompt.md`
   - Move `[Unreleased]` entries under new version header in `CHANGELOG.md`
   - Add `### Changed` entry documenting the milestone archive
4. **Push & Release**:
   - `git add` all changed files
   - `git commit -m "chore: milestone N archive and bump to vX.Y.Z"`
   - `git push origin main`
   - `git tag vX.Y.Z && git push origin vX.Y.Z`
   - `gh release create vX.Y.Z --title "vX.Y.Z -- <title>" --notes "<changelog>"`
