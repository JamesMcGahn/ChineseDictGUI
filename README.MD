# Chinese Dict

## Description

Chinese Dictionary App for managing sentences, lessons and words from a chinese learning podcast source.

## TO-DOs and FEATURES

### TODO - remove logger creation in base worker classes, use signal

### TODO - use LOGLEVEL enum instead of strings

### TODO - disconnect audio threads from pages move to a manager

### TODO - disconnect whisper and combine audio threads from page to manager

### FEATURE - Settings Page

- login information
- logging settings
- whisper settings

### FEATURE - Lessons Search

- search for lessons based on date and level
- pass selected lessons from results to lesson scraper
- store previously scraped lessons

### FEATURE - Anki Sync

- ~~inital import~~
  - ~~ask user for anki deck names and check that it exists~~
- ~~from anki to local db~~
- ~~from local db to anki~~
- Set scheduler for anki import export
- refactor / clean up code

### FEATURE - Pull New Words from Apple Notes

### FEATURE - Add words offline via cc-edict dictionary

    - ability to update dictionary with new copy downloaded

### FEATURE - Ability to manaully add words and sentences

    - via pop up dialog
    - via csv or excel file

### FEATURE - show user progess on long tasks

    - Audio Threads
    - Scraping Threads
    - Anki Syncs and Imports
