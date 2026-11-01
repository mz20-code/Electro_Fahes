"""Package the runnable source without private runtime data or old environments."""
from pathlib import Path
import sys
import zipfile

root = Path(__file__).resolve().parents[2]
destination = Path(sys.argv[1]).resolve()
if destination.is_relative_to(root):
    raise SystemExit("Choose a destination outside the source folder.")
skip = {".venv", "venv", "node_modules", "__pycache__", ".pytest_cache", ".git", "instance"}
with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
    for file in sorted(root.rglob("*")):
        if not file.is_file():
            continue
        relative = file.relative_to(root)
        if any(part in skip for part in relative.parts):
            continue
        if file.name == ".env" or file.suffix in {".pyc", ".pyo", ".db", ".sqlite", ".sqlite3", ".key"}:
            continue
        name = Path(root.name) / relative
        data = file.read_bytes()
        if file.suffix.lower() == ".bat":
            data = data.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
        archive.writestr(str(name), data)
    assert archive.testzip() is None
print(f"Packaged {destination.name}: {destination.stat().st_size / 1048576:.1f} MiB")
