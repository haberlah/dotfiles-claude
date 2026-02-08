# Prompt Templates

## Planning Prompt (Prompt 0)

Use Plan Mode. Establishes full project context.

```
## Prompt 0: Planning Phase

> **Switch to Plan Mode before pasting**

[PROJECT NAME]

I want to build [brief description].

## Project Overview
[2-3 sentences]

## Core Features
1. [Feature 1]
2. [Feature 2]
3. [Feature 3]

## Technical Stack
- Frontend: [framework]
- Backend: [framework/runtime]
- Database: Replit Database (PostgreSQL)
- Storage: Replit App Storage (if needed)

## Database Schema Overview
[List main tables and relationships]

## Architecture Patterns
- State management: [approach]
- API structure: [REST/etc]
- Component organization: [pattern]

## Key Constraints
[Any specific requirements]

Please confirm you understand. Do not build yet.

**After confirmation:** Switch to Build Mode for Prompt 1.
```

## Build Prompt Template (Prompts 1-N)

Use Build Mode. Each phase should be self-contained and testable.

```
## Prompt N: [Phase Name]

> **Use Build Mode**

[OBJECTIVE]
One sentence: what this phase accomplishes.

[REQUIREMENTS]
1. [Specific, actionable requirement]
2. [Specific, actionable requirement]
3. [Specific, actionable requirement]

[TECHNICAL DETAILS]
Database (if applicable):
- Table: [name] with fields [list]

API endpoints (if applicable):
- METHOD /path - description

Components (if applicable):
- ComponentName: [purpose]

[INTEGRATION]
- Use [hook/component] from Phase N
- Add to [location] from Phase N

[DO NOT CHANGE] (if applicable)
- [Protected functionality]

**Acceptance Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Previous functionality still works

**Create checkpoint: "[Phase name]"**
```

## Phase Sizing

Each prompt should:
- Make meaningful progress
- End with testable functionality
- Not leave half-built states
- Take 5-15 minutes for Agent

## Dependency Ordering

Establish foundations before dependent features:

```
Phase 1: Setup, database schema, storage → Foundation
Phase 2: Core data models, basic CRUD → Requires Phase 1
Phase 3: Primary features → Requires Phase 2
Phase 4: Secondary features → Requires Phase 2/3
Phase 5: UI/UX refinements → Requires core features
Phase 6: Polish, deployment → Requires all above
```

## Architectural Points to Establish Early

```
□ Database schema (all tables)
□ State management pattern
□ Reusable hooks/utilities
□ Layout structure
□ API route patterns
□ Shared resources (contexts, refs)
```

---

## Example: Audio Library App

### Prompt 0 (Plan Mode)

```
Audio Library Visualiser

I want to build a personal audio library with real-time visualisation.

## Project Overview
Web app for uploading, organizing, and playing audio files with frequency visualisation.

## Core Features
1. Audio file upload and library management
2. Audio playback with transport controls
3. Real-time frequency visualisation
4. Playlist management

## Technical Stack
- Frontend: React with Vite
- Backend: Express.js
- Database: Replit Database (PostgreSQL with Drizzle)
- Storage: Replit App Storage

## Database Schema
- tracks: id, title, artist, duration, storageKey, createdAt
- playlists: id, name, createdAt
- playlist_tracks: playlistId, trackId, position

## Architecture
- State: React Context for audio state
- API: RESTful under /api
- Components: pages/, components/, hooks/, lib/

Please confirm understanding. Do not build yet.
```

### Prompt 1 (Build Mode)

```
[OBJECTIVE]
Set up project structure, database schema, and storage.

[REQUIREMENTS]
1. Initialize React + Vite frontend with Express backend
2. Configure Replit Database with Drizzle ORM
3. Create all database tables
4. Set up Replit App Storage bucket
5. Create basic layout with sidebar and main area

[TECHNICAL DETAILS]
Database:
- tracks: id (serial), title (text), artist (text), duration (int), storageKey (text), createdAt (timestamp)
- playlists: id (serial), name (text), createdAt (timestamp)
- playlist_tracks: playlistId (FK), trackId (FK), position (int)

Layout:
- Sidebar (250px): navigation
- Main area: content
- Footer (80px): player placeholder

**Acceptance Criteria:**
- [ ] App runs without errors
- [ ] Database tables accessible
- [ ] App Storage configured
- [ ] Layout displays correctly

**Create checkpoint: "Foundation"**
```
