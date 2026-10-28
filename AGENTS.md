# Maintaining paper-figure-reconstruction

- This repository is the source of truth. Make changes here, test them, and only sync the global installed Skill when requested. Do not silently overwrite local installed edits; use the backup-capable installer.
- Preserve user intent: actual Blender geometry for 3D, native text/paths for 2D, explicit own-render raster provenance, source-based iterations. Never replace a reconstruction with a screenshot wrapper or claim 1:1 from a metric alone.
- Read SKILL.md and the relevant reference before changes. Keep entrypoint guidance concise; document a workaround only when supported by observed evidence. Do not hardcode a particular user's home directory.
- For a bug, first capture a minimal reproducer, then make a focused fix and a behavioral regression test. Run `python -m unittest discover -s tests -v`; render and inspect affected SVG output. Application adapter changes need actual app verification when available. State unexecuted checks precisely.
- Never launch Blender/Illustrator in unit tests. Check local execution instructions; on the originally tested Mac, Blender 4.5.10 requires approved execution outside the sandbox during Metal detection. Use the dry-run command, not repeated startup-crash retries.
- Serialize Illustrator scripts, restore interaction state in finally, preserve user documents, and inspect live state before retrying a timeout. Do not force-quit an app with potentially unsaved user work without authorization.
- Do not install software, modify MCP settings, upload paper assets or remove copyright marks as an incidental part of a fix. Keep large BLEND/AI files and private logs outside git; use original minimal examples in issues/tests.
- Verify both visuals and semantics. Include component/panel checks; preserve protected regions. Record the actual SSIM variant and contour method, and disclose inferred physical geometry.
- Before publishing, inspect the diff and tracked file list for private paths, credentials and unlicensed reference assets. Keep README usage/troubleshooting consistent with actual flags. Avoid claiming cross-platform or software-version coverage beyond tests.
- Report the issue fixed, relevant tests, residual limitations, commit/PR, and whether the installed global copy was updated. Do not promise automatic monitoring of future issues.
