from src.parser import KeepParser

parser = KeepParser("tests/Takeout/Keep")

files = parser.get_keepjson_files()
notes = parser.create_notes()

print(f"Loaded {len(notes)} notes.")
print()

print(notes[0])

