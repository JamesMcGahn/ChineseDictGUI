# Chinese Dict

## Description

Chinese Dictionary App for managing sentences, lessons and words from a chinese learning podcast source.

# Project Roadmap – To-Dos & Features

Legend:

- [ ] Not started
- [/] In progress
- [x] Done

Priorities:

- 🔥 High
- ⭐ Medium
- ⬜ Low

---

# Core Architecture Refactor

## Network Refactor – Unified Response

- [x] Define unified network result shape:

  - [x] `ok: bool`
  - [x] `status: int` (`0` = no HTTP response)
  - [x] `data: dict | None`
  - [x] `message: str | None`
  - [x] `raw: Response | None`

- [x] Update Networker to emit **one object** (`Signal(object)`)

  - [x] Normalize success responses into unified shape
  - [x] Normalize error responses into unified shape
  - [x] Never emit `None` at the top level

- [x] Add safe helpers in Networker:

  - [x] `safe_extract_json(response)`

- [ ] Migrate consumers incrementally:
  - [ ] Replace `response.status_code` → `result["status"]`
  - [ ] Replace `response.json()` → `result["data"]`
  - [ ] Replace exception handling → `result["message"]`
  - [ ] Remove `if response is None` checks

## Database System Refactor 🔥

- [ ] Convert `DatabaseManager` into a **stateless utility**.
- [ ] Make `connect()` return **a fresh SQLite connection per worker**.
- [ ] Update workers to:
  - [ ] Create their own DB connection via `db_manager.connect()`
  - [ ] Pass `(db_manager, connection)` into all DAL operations
- [ ] Update all DAL classes to accept `(db_manager, connection)`
- [ ] Remove `self.connection` from `DatabaseManager`
- [ ] Evaluate whether the **global DB mutex** is still needed or can be simplified

# Threading & Worker Cleanup

## Worker + QThread Improvements 🔥

- [ ] Replace implicit logger usage in workers with **logger signals**
- [ ] Implement a unified `WorkerBase`:
  - [ ] `start_work()` slot
  - [ ] `finished` signal
  - [ ] `error` signal
  - [ ] DB cleanup in thread teardown
- [ ] Create a **WorkerManager** to handle:
  - [ ] Audio workers
  - [ ] Whisper/Faster-Whisper workers
  - [ ] Scraper workers
  - [ ] Database workers
- [ ] Remove direct worker ownership from UI pages
- [ ] UI should only receive signals from WorkerManager

# Settings & Configuration

## Settings Page ⭐

- [ ] Login settings (ChinesePod, LingQ, etc.)
- [ ] Logging settings
- [ ] Whisper/Faster-Whisper settings
- [ ] Persist everything via **QSettings**
- [ ] Apply settings through a global **AppContext** helper

## Logging System Improvements ⭐

- [ ] move enum to base enum module
- [ ] Replace string log levels with `LOGLEVEL` Enum
- [ ] Improve formatting of log events
- [ ] Ensure logger thread writes during shutdown reliably

# Audio & Transcription Pipeline

## Audio Thread Consolidation 🔥

- [ ] Combine Whisper + audio processing under a single **AudioManager**
- [ ] Remove thread logic from UI pages
- [ ] Add granular progress/error signals for:
  - [ ] Dialogue extraction
  - [ ] Vocabulary extraction
  - [ ] Grammar extraction
  - [ ] Expansion extraction
  - [ ] Whisper transcription

# Lesson Search & Scraping

## Lesson Search Feature ⭐

- [ ] Search lessons by date
- [ ] Search lessons by level
- [ ] Display search results in UI
- [ ] Send selected lessons to scraper worker
- [ ] Track previously scraped lessons in DB
- [ ] Add "Force re-scrape" option

# Anki Sync Pipeline

## Sync Improvements 🔥

- [x] Initial import
- [x] Anki → Local DB sync
- [x] Local DB → Anki sync
- [ ] Add scheduled background auto-sync
- [ ] Improve conflict handling
- [ ] Refactor sync logic for readability
- [ ] Add UI progress feedback for each sync stage

# Word & Sentence Management

## Apple Notes Import ⭐

- [ ] Extract words from Apple Notes
- [ ] Deduplicate extracted words
- [ ] Insert into DB (+ optional add to Anki)
- [ ] Show UI approval dialog before insertion

## CC-EDICT Dictionary Support ⭐

- [ ] Load CC-EDICT file offline
- [ ] Word lookup UI
- [ ] Optional dictionary update mechanism

## Manual Entry Tools ⬜

- [ ] Manual word entry dialog
- [ ] Manual sentence entry dialog
- [ ] CSV import tool
- [ ] Excel import tool
- [ ] Validate entries before saving

# Unified Progress UX

## Progress System 🔥

Create a **generic progress pipeline** for all slow operations:

- [ ] Audio extraction
- [ ] Lesson scraping
- [ ] Whisper transcription
- [ ] Anki sync (all phases)
- [ ] Bulk inserts
- [ ] Apple Notes import

# General Cleanup

## Architecture Cleanup ⭐

- [ ] Move service initialization from `MainWindow` → `AppInitializer`
- [ ] Improve folder structure (e.g., `core/`, `services/`, `workers/`, `ui/components/`)
- [ ] Remove unused imports
- [ ] Add error dialogs for network/login failures
- [ ] Expand README with a clear **architecture overview**
- [ ] remove print statements / convert to logger
  - [ ] Networker

# Optional Future Features

## Nice-to-Haves ⬜

- [ ] Dedicated queued DB thread
- [ ] YouTube → Whisper → Anki pipeline
- [ ] Grammar pattern detection engine
- [ ] Improved packaging (Nuitka, PyInstaller, fbs)
