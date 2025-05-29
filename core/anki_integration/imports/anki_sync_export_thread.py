# step 1 connect to database
# step 2 query integration information -
# step 3 check if initial baseline sync was completed
# step 4 figure out the time difference between last sync
# step 5 query edited/new records from local db for this time interval
# - WHERE anki_id IS NULL OR local_update > anki_update
# step 6 check if record local update is >= anki_update
# step 7 export notes to anki
# - Use addNotes for new
# - Use updateNoteFields for updates
# step 8: Update local DB records
# - Set anki_id (if new)
# - Set anki_update = now()
# step 9: Update integration table with current timestamp
# step 10: Signal sync complete
