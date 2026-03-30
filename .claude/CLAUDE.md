# CLAUDE.md — 2D Zombie Shooter Game

## Project Overview
This is a 2D zombie shooter game built using Cursor with Claude Code as the AI development assistant.
The goal is a fun, playable, and well-structured game with clean code that doesn't break between sessions.

**Principles:** *Organization sells* — neat structure and naming signal quality; *format = effortless* — layouts, docs, and UI should scan instantly without mental effort.

---

## Tech Stack
- **Engine/Framework:** Phaser 3 (recommended — browser-based, great for 2D shooters, huge community)
- **Language:** JavaScript (or TypeScript if we upgrade later)
- **Rendering:** Canvas via Phaser 3
- **Package Manager:** npm
- **Version Control:** Git (commit after every completed task)

> If the stack changes, update this section immediately before continuing any work.

---

## Game Structure (File Layout)
```
/src
  /scenes        → GameScene, MenuScene, GameOverScene
  /entities      → Player.js, Zombie.js, Bullet.js
  /systems       → CollisionSystem.js, SpawnSystem.js, ScoreSystem.js
  /ui            → HUD.js, HealthBar.js
  /assets        → /sprites, /audio, /tilemaps
  /config        → gameConfig.js, constants.js
index.html
main.js
```

---

## Core Game Rules (Do Not Change Without Asking)
- Player moves with WASD, aims with mouse, shoots with left click
- Zombies spawn in waves, increasing in number and speed each wave
- Player has health points — contact with zombies reduces HP
- Game ends when HP reaches 0
- Score increases per zombie killed
- These rules are LOCKED unless William explicitly says to change them

---

## Claude's Workflow Rules (ENFORCED)

### ALWAYS follow this order — no exceptions:
1. **BRAINSTORM** — Ask clarifying questions before touching any code
2. **PLAN** — Write out a step-by-step implementation plan with file paths
3. **CODE** — Implement one task at a time, not everything at once
4. **TEST** — Verify the feature works before moving to the next task
5. **REVIEW** — Check for bugs, broken logic, or side effects
6. **COMMIT** — Suggest a git commit message after each completed feature

### NEVER do the following:
- Do NOT start coding without a written plan first
- Do NOT change game rules or core mechanics without asking William
- Do NOT refactor working code unless asked
- Do NOT add new features while fixing a bug
- Do NOT skip testing a feature before moving on
- Do NOT assume — if something is unclear, ask first

---

## Coding Standards
- Keep files small and focused — one system per file
- Use clear, simple variable names (no clever abbreviations)
- Add a comment above every function explaining what it does
- No hardcoded values — use `/config/constants.js` for all numbers (speed, HP, spawn rate, etc.)
- Every new feature needs at least one basic test or manual verification step

---

## Session Continuity
- At the start of every session, read this file completely
- Check `/docs/progress.md` for what was last completed
- Do not assume anything was finished — verify it
- At the end of every session, update `/docs/progress.md` with:
  - What was completed
  - What is in progress
  - What's next
  - Any known bugs or blockers

---

## Priority Order When Conflicts Arise
1. Working game (playable > perfect)
2. Clean structure (organized > clever)
3. Visual polish (looks good > looks amazing)
4. New features (only after current feature is stable)

---

## Current Build Status
- [ ] Project setup and Phaser 3 installed
- [ ] Player movement and shooting
- [ ] Zombie spawning system
- [ ] Collision detection (bullets + zombies, zombies + player)
- [ ] Health system
- [ ] Score system
- [ ] Wave system
- [ ] Game over screen
- [ ] Main menu
- [ ] Sound effects
- [ ] Visual polish

> Check off items as they are completed. Do not skip ahead.

---

## Notes from William
- I am not a developer — keep explanations simple and practical
- When something breaks, explain what broke and why in plain English
- Always suggest the simplest fix first before a complex one
- If you're about to do something big or risky, stop and ask first
