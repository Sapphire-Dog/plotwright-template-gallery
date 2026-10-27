#!/usr/bin/env python3
"""Adds a template set to the gallery, from the email Share Template... wrote or from the set's file.

    scripts/add-set.py "Template set for the gallery- Fantasy World.eml"
    scripts/add-set.py "Fantasy World.wttemplates" --author "Mara Voss" --description "For epic fantasy."

From an email (drag it from Mail to the Finder to save it as a .eml file), the set is the attached
.wttemplates file, and the author and description come from the email's text. Either can be
given or changed with --author and --description.

It checks the set opens as a Writers Toolbox template set, copies it to sets/ under a name made
from the set's (fantasy-world.wttemplates), and adds its entry to index.json, or updates it if
the set is already there. Then it shows the change. --commit commits it, and --push pushes too.
"""
import argparse, datetime, email, email.policy, json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.json"
SETS = ROOT / "sets"


def from_email(path):
    message = email.message_from_bytes(path.read_bytes(), policy=email.policy.default)
    attachment = None
    for part in message.iter_attachments():
        if (part.get_filename() or "").endswith(".wttemplates"):
            attachment = (part.get_filename(), part.get_content() if isinstance(part.get_content(), bytes) else part.get_payload(decode=True))
    if attachment is None:
        sys.exit("The email has no .wttemplates file attached.")
    body = message.get_body(preferencelist=("plain",))
    text = body.get_content() if body else ""
    author = re.search(r"^By: (.+)$", text, re.M)
    author = author.group(1).strip() if author else None
    if author == "(no name given)":
        author = None
    note = re.search(r"What it's for:\s*\n(.*?)(?:\n---|\Z)", text, re.S)
    note = note.group(1).strip() if note else None
    if note == "(no note)":
        note = None
    return attachment[1], author, note


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "set"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("file", type=Path, help="the email (.eml) or the set (.wttemplates)")
    parser.add_argument("--author", help="who made it, as the gallery shows it")
    parser.add_argument("--description", help="what it's for, in a sentence or two")
    parser.add_argument("--id", help="the set's id in the list (made from its name if not given)")
    parser.add_argument("--commit", action="store_true", help="commit the change")
    parser.add_argument("--push", action="store_true", help="commit and push the change")
    args = parser.parse_args()

    if args.file.suffix.lower() == ".eml":
        data, author, note = from_email(args.file)
    else:
        data, author, note = args.file.read_bytes(), None, None
    author = args.author if args.author is not None else author
    note = args.description if args.description is not None else note

    try:
        content = json.loads(data)
    except ValueError:
        sys.exit("The set isn't a Writers Toolbox template file: it doesn't read as JSON.")
    templates = [t.get("name", "") for t in content.get("templates", []) if t.get("name")]
    name = (content.get("set") or {}).get("name")
    if not templates:
        sys.exit("The set has no templates in it.")
    if not name:
        sys.exit("The file is templates, not a template set; it needs to be shared from Template Sets.")

    identifier = args.id or slug(name)
    target = SETS / f"{identifier}.wttemplates"
    SETS.mkdir(exist_ok=True)
    target.write_bytes(data)

    index = json.loads(INDEX.read_text())
    existing = next((i for i, s in enumerate(index["sets"]) if s.get("id") == identifier), None)
    # Updating a set keeps what the list already says unless something new is given.
    if existing is not None:
        before = index["sets"][existing]
        author = author if author is not None else before.get("author")
        note = note if note is not None else before.get("description")
    entry = {"id": identifier, "name": name}
    if author:
        entry["author"] = author
    entry["description"] = note or ""
    entry["file"] = f"sets/{identifier}.wttemplates"
    entry["templates"] = templates
    entry["updated"] = datetime.date.today().isoformat()
    if existing is None:
        index["sets"].append(entry)
        verb = "Added"
    else:
        index["sets"][existing] = entry
        verb = "Updated"
    index["sets"].sort(key=lambda s: s["name"].lower())
    INDEX.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n")

    print(f"{verb} “{name}”{' by ' + author if author else ''}: {', '.join(templates)}")
    print(f"  {target.relative_to(ROOT)}")
    if not note:
        print("  No description yet: add one with --description, or in index.json.")
    if args.commit or args.push:
        subprocess.run(["git", "-C", str(ROOT), "add", str(target), str(INDEX)], check=True)
        subprocess.run(["git", "-C", str(ROOT), "commit", "-q", "-m", f"{verb} the {name} template set"], check=True)
        if args.push:
            subprocess.run(["git", "-C", str(ROOT), "push", "-q"], check=True)
        print("Committed" + (" and pushed; the gallery shows it within a few minutes." if args.push else "; push when ready."))
    else:
        print("Check it with: git diff. Then run again with --push, or commit and push yourself.")


if __name__ == "__main__":
    main()
