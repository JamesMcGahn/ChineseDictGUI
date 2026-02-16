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

- [/] Migrate consumers incrementally -> NetworkResponse Model:
  - [ ] Replace `response.status_code` → `result.status`
  - [ ] Replace `response.json()` → `result.data`
  - [ ] Replace exception handling → `result.message`
  - [ ] Remove `if response is None` checks

## Database System Refactor 🔥

- [x] Create two services Read & Write
- [x] Clean Up DALS
  - [x] Standardize DALs with Base Class
  - [x] Remove passing cursor back to services
    - [x] Read Services
    - [x] Write Services
- [x] DBResponse Model
  - [x] Responses for all Write Methods
  - [x] Responses for all Read Methods
- [x] DBJob Model
  - [x] Payloads for all Write Methods
- [x] Read Services
  - [x] - rewrite methods to handle DAL rewrites
  - [x] - short lived new connection managed by DBManager
  - [x] - base class
  - [x] - implement base class for each table's read service
- [x] Write Services
  - [x] - rewrite methods to handle DAL rewrites
  - [x] - long lived connection managed by write thread
  - [x] - base class
  - [x] - implement base class for each table's read service
  - [x] Write Services - queue based long lived thread -> connection managed by Thread
- [ ] Migrate consumers incrementally -> Service Model

# Threading & Worker Cleanup

## Worker + QThread Improvements 🔥

- [ ] Replace implicit logger usage in workers with **logger signals**
- [ ] Implement a unified `WorkerBase`:
  - [ ] `start_work()` slot
  - [ ] `finished` signal
  - [ ] `error` signal
  - [ ] DB cleanup in thread teardown
- [/] Create a **WorkerManager** to handle:
  - [x] Audio workers
  - [x] Whisper/Faster-Whisper workers
  - [/] Scraper workers
  - [ ] Database workers
- [/] Remove direct worker ownership from UI pages
- [ ] UI should only receive signals from WorkerManager

# Settings & Configuration

## Settings Page ⭐

- [ ] Login settings (ChinesePod, LingQ, etc.)
- [x] Logging settings
- [/] Whisper/Faster-Whisper settings
- [x] Persist everything via **QSettings**
- [ ] Apply settings through a global **AppContext** helper

## Logging System Improvements ⭐

- [ ] move enum to base enum module
- [ ] Replace string log levels with `LOGLEVEL` Enum
- [ ] Improve formatting of log events
- [ ] Ensure logger thread writes during shutdown reliably

# Audio & Transcription Pipeline

## Audio Thread Consolidation 🔥

- [x] Combine Whisper + audio processing under a single **AudioManager**
- [/] Remove thread logic from UI pages

## Lesson Workflow Pipeline

- [x] Remove Lesson thread logic from lesson page
- [/] Workflow for lesson using jobs
  - [x] spec generation / job generation controller
  - [/] clean up controller
- [x] Add lingqq Lesson jobs to controller (waiting to be built)
- [x] Add db job to controller (waiting to be built)
- [ ] create model for "spec" / or use the queue model
- [ ] update project status
  - [ ] add progress fn / signal for lesson overall status
- [ ] Queue Feature
  - [ ] pick up progress from any part of the process
- [ ] handle errors from any part of the process

## Word Workflow Pipeline

- Remove Word logic from page
- [ ] WordTask enum
- [ ] Expand WORD model
  - [ ] queue_id, status, task, example sentences, source
- [ ] refactor Word Worker
  - [ ] Use token from context TokenWorker
  - [ ] add fallback to request on stale token
  - Split logic for mgdb and cpod from one single worker -
    - handle in worklow
- [ ] Option for "Word" List lessons for Lingq (word + example sentences)
  - [ ] add example sentences to word model
  - [ ] add source to word model?
- [ ] add progress for word status

## Lingqq Lesson Auto Submission

- [x] Create login worker
  - [x] extract cookies / auth token
- [x] Create worker to obtain collection ids
- [x] Lesson Submission Worker
- [x] create fn to obtain crsf token
- [x] create fn to submit lesson
- [x] design and implement new job service structure

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

- [x] Move service initialization from `MainWindow` → `Context`
- [ ] Improve folder structure (e.g., `core/`, `services/`, `workers/`, `ui/components/`)
- [ ] Remove unused imports
- [ ] Add error dialogs for network/login failures
- [ ] Expand README with a clear **architecture overview**
- [ ] remove print statements / convert to logger
  - [ ] Networker

# Optional Future Features

## Nice-to-Haves ⬜

- [x] Dedicated queued DB thread
- [ ] YouTube → Whisper → Anki pipeline
- [ ] Grammar pattern detection engine
- [ ] Improved packaging (Nuitka, PyInstaller, fbs)
- [ ] Log Detail Level

## Progress Bar / Signals

- [ ] Add granular progress signals for:
  - [ ] Lesson Workflow
  - [ ] Whisper transcription
  - [ ]
