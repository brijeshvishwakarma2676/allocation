# Project Memory — Naigaon Allocation System

**Client:** House of Abhinandan Lodha  
**Property:** Residential Development, Naigaon  
**Source:** `memory/core/Allocation Logic Confidential.pdf`

This directory is the persistent knowledge base for the allocation project.

---

## Quick Reference

| What | Where |
|------|-------|
| Business requirements & stakeholders | `docs/brd.md` |
| Feature list (P0/P1/P2) | `docs/prd.md` |
| Tower sequence, band logic, architecture | `docs/architecture.md` |
| Full algorithm spec with pseudocode | `docs/allocation-algorithm.md` |
| User stories (all roles) | `docs/user-stories.md` |
| Database schema | `docs/database.md` |
| API endpoints | `docs/api-specs.md` |
| Deployment environments | `docs/deployment.md` |
| Implementation backlog | `tasks/backlog.md` |
| Bug tracker | `tasks/bugs.md` |
| Key decisions and rationale | `progress/decisions.md` |
| Current project status | `progress/current-status.md` |
| Changelog | `progress/changelog.md` |
| Diagrams, wireframes, screenshots | `assets/` |

---

## Key Numbers at a Glance

- **2,223 units** across **9 active towers** (Day 1)
- **35 floors** per tower, **8 units** per floor
- **4 bands** (7 floors each): B5 (29–35), B4 (22–28), B3 (15–21), B1+B2 (01–14)
- **3 customers** pre-allocated per unit, **10 max** at any time
- **15 min** inactivity → dummy customer triggers
- **30 min** hold per customer slot
- Allocation Day 1: **28th Sep** | Day 2: **2nd Oct**
