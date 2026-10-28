# Application adapters

## Blender
On this Mac Blender 4.5.10 fails inside the restricted sandbox during Metal detection. CPU rendering does not fix startup detection. Obtain required approval and run outside the sandbox from the outset:
```
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --disable-autoexec --python-exit-code 1 --python SCRIPT -- --spec SPEC --out OUTPUT
```
The runner's dry-run emits arguments; it does not grant permission. Do not retry startup segfaults or reset preferences blindly. Separate startup, Python, render and export failures; keep logs. On other hosts inspect local guidance rather than assuming this workaround applies universally. Never load untrusted auto-execution.

## Illustrator
Prefer a verified available connector if it supports native editable objects and saving. Otherwise generate JSX with `figure.py illustrator`; it validates SVG before opening a new document, assigns component groups to layers, embeds own-render assets, saves AI/PNG and a native-object manifest. Execute generated script with file-based AppleScript:
```
with timeout of 300 seconds
 tell application id "com.adobe.illustrator"
  do javascript file (POSIX file "/absolute/path/import.jsx")
 end tell
end timeout
```
Run application commands through the required approval mechanism. Serialize jobs. A timeout does not prove the process stopped; inspect outputs and application state before retrying. Script restores `app.userInteractionLevel` in `finally`, closes only its created document, and preserves existing user documents. The helper rejects an SVG already open in Illustrator. Use unique test copies for editability checks. After reopening AI, inspect native text, paths, layers and raster count, and change text/path geometry in a disposable copy. Font substitution and missing mathematical glyphs require visual checks even when counts pass.

## Runtime
Use a known interpreter with NumPy/Pillow; don't install into system Python or Conda base. `doctor` reports missing packages. The SVG renderer resolves Sharp from `PFR_NODE_MODULES`, ordinary Node resolution, or the existing Codex bundled runtime. No npm/pip installs are performed. PDF input can use an existing Poppler installation. If dependencies are absent, report the precise missing capability and ask before installation.

Observed Illustrator 30.4 behavior: marker-bearing SVG lines lost their shafts during import even though text/path counts looked valid. The SVG helper emits explicit editable shaft/head groups instead. Visually check arrows after import; a successful save is insufficient.

A hybrid SVG containing an embedded data-URI image stalled in Illustrator 30.4 during this test (AppleEvent timeout, sustained CPU); process sample retained in local test evidence. This does not diagnose all Illustrator hangs. The adapter now imports a vector-only SVG with named placeholders, then places/embeds each validated own-render PNG using Illustrator APIs at the placeholder bounds and stacking position. Do not open hybrid data-URI SVG directly through this adapter. If the application is unresponsive, inspect it before any retry; never terminate it when user work might be unsaved without permission.
