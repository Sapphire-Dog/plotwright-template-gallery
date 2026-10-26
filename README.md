# Writers Toolbox Template Gallery

Template sets writers have shared for Writers Toolbox, from [Sapphire Dog](https://sapphiredog.com). The app's
**Template Gallery** reads `index.json` from this repository and shows each set listed there,
with its templates, to add to a library.

## Sharing a set

In Writers Toolbox, open **Templates › Share and Template Sets › Template Sets…**, and choose
**Share…** beside a set. Add your name and a note on what it's for, and send the email that
opens, with the set attached. Once it's looked over, it's added here.

## Adding a set (for maintainers)

1. Save the `.wttemplates` file from the email into `sets/`, named in lowercase with hyphens,
   such as `sets/fantasy-world.wttemplates`. Open it in Writers Toolbox first (Templates ›
   Import Templates…) to check it reads and looks right.
2. Add an entry to `sets` in `index.json`:

   ```json
   {
     "id": "fantasy-world",
     "name": "Fantasy World",
     "author": "Mara Voss",
     "description": "Characters, kingdoms, magic systems and creatures for epic fantasy.",
     "file": "sets/fantasy-world.wttemplates",
     "templates": ["Character", "Kingdom", "Magic System", "Creature"],
     "updated": "2026-10-26"
   }
   ```

   - `id` stays the same when the set is updated; use the file's name without `.wttemplates`.
   - `author` is optional; leave it out if the writer didn't give a name.
   - `templates` lists its templates' names, shown before the file is fetched.
   - `updated` is the day it was added or last replaced, as year-month-day.
3. Commit to `main`. The app reads the list fresh each time the gallery opens, so it shows at
   once (GitHub can take a few minutes to serve the new files).

To update a set, replace its file and change `updated`. To take one down, remove its entry and
its file.

## The list's format

`index.json` has `formatVersion` (1) and `sets`, an array of entries as above. A list with a
higher `formatVersion` tells older versions of the app to update. The app only reads files
under this repository that end in `.wttemplates`.
