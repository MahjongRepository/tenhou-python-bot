I wanted to build a flow like this:

- In bots runner we download previous bot release from GitHub.
We unpack code and import it.
- We run 3 old copy vs one new copy of AI logic.

But I wasn't able to accompish this with Python imports.

Maybe some day I will do it,
but for now we will have a separate file with old ai version.

This is `ai/old_version.py`, you need to create it manually and copy into it old logic from previous release.