##########################
To create a new language
##########################

Translations are available on transifex under::

    https://www.transifex.com/projects/p/RhodeCode/

Log into transifex and request new language translation.

manual creation of new language
+++++++++++++++++++++++++++++++

**Step 1:** If you don't have a dev environment set up, download sources of
RhodeCode. Run::

    python setup.py develop

Otherwise, update to the latest stable commit.


**Note:** The following commands are intended to be run in the main repo directory
using Linux; running them in nix-shell is fine.


**Step 2:** Make sure all translation strings are extracted by running::

    python setup.py extract_messages


**Step 3:** Create a new language by executing following command::

    python setup.py init_catalog -l <new_language_code>

This creates a new language under directory rhodecode/i18n/<new_language_code>


**Step 4:** Be sure to update transifex mapping, located at rhodecode/.tx/config
The path to the new language should be identical to the others, instead using
the new language code.


**Step 5:** Verify the translation file and fix any errors.
This can be done by executing::

    msgfmt -f -c rhodecode/i18n/<new_language_code>/LC_MESSAGES/<updated_file.po>

Edit rhodecode/i18n/<new_language_code>/LC_MESSAGES/rhodecode.po for errors
with your favorite file editor (the errors will tell you what's missing, check
other rhodecode.po files in existing languages for clues).


**Step 6:** Finally, compile the translations::

    python setup.py compile_catalog -l <new_language_code>

**Note:** Make sure there is not a .mo file in the top-level folder!


##########################
To update translations
##########################

**Note:** This is a different process, not needed when you are adding a translation.

**Step 1:** Fetch the latest version of strings for translation by running::

    python setup.py extract_messages


**Step 2:** Update the rhodecode.po file using::

    python setup.py update_catalog -l <new_language_code>


**Step 3:** Update the po file as outlined in step 5 for new translations (see above).


**Step 4:** Compile the translations as outlined in step 6 for new translations (see above).

**Note:** Make sure there is not a .mo file in the top-level folder!


###########################
Javascript translations
###########################

First find all translation used in JS by running the command:

    grep "_TM\[.*\]" -R . -oh | sort -u

Then compare it against the file scripts/tasks/file_generation/js_i18n_data.py.
Add or remove strings to that file remembering to add them surrounded by _(...),
or otherwise they won't get added to the catalog.

In case the file changed, regenereate the catalog by following the
instructions above ('to update translations').

Once the new strings were transalated and the catalogs comiled with msgfmt, you
can generate the Javascript translation files. To do so, just run the command:

    invoke -r scripts/  generate.js-i18n

Which will generate one JS file for detected language in the folder
rhodecode/public/js/rhodecode/i18n/{lang}.js

Finally, commit the changes.


########################
Testing translations
########################

Edit the test.ini file, setting the lang attribute to::

    lang=<new_language_code>

Run RhodeCode tests by executing::

    nosetests

###########################
Workflow for Transifex
###########################

#0 new language:
   edit .tx/config and add language
#1 extract messages to generate updated pot file
    python setup.py extract_messages
#2 push source .pot file to Transifex
    tx push -s
#3 when translations are ok pull changes
    tx pull
#4 compile languages
    python setup.py compile_catalog

