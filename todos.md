# TO-DOS and FEATURES

FEATURE: add CLI option to download audio of words and/or sentences or dialogues

FEATURE: Get definition for single word

    - check dictionary for word, if found return the definition
    - if word not found, ask to scrape word
    - ask to save word etc.

FEATURE: print dictionary to file - done -- needs to be cleaned up

FEATURE: update dictionary - delete words

FEATURE: print sentences to file

FEATURE: option to just get example sentences for a word

FEATURE: Quitting the APP

    - ✅ Quit Option on initial run - Quit option on keyboard interrupt
    - any time during a scrape or audio dl loop
    - any time the main app runs

FEATURE: Load initial sentences and words

    - 🔨 words - working but needs to be improved
    - sentences - check dictionary, if none exists ask user if they want to load on start of app

FEATURE: ask user for creds on init of app

    - save them as pickle
    - check on load of app for creds

TODO: bad sign in/session

    - let user know and ask them to re-enter credentials

TODO: handle if there are no sentences

TODO: error handling for audio download

TODO: APP Clean up

    - TODO: 🔨 Start code
    - TODO: 🔨 Clean up code accross app
