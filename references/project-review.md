# Reference project review — 2026-10-28

Reviewed public README, license and dependency manifests. These are capability/documentation reviews, not execution audits. No third-party source has been copied into this skill.

- https://github.com/Yingqi-Han/reconstruct-scientific-svg-skill — MIT, copyright Yingqi-Han. Semantic SVG reconstruction and native text/image audits; comparator requires NumPy, Pillow, scikit-image and a separate SVG renderer. Useful distinction: raster wrapper vs native vector vs outlined text vs editable text. Not a Blender geometry reconstruction engine.
- https://github.com/lgwrightlab/schematic-figure — MIT, copyright Jinchen Zhao and Logan Wright. Diagram generation with Node >=22 and Chromium, optional Blender/RDKit; design workflow rather than guaranteed inverse reconstruction. Bundled Latin Modern fonts have a separate GUST Font License. No fonts bundled here.
- https://github.com/ahujasid/blender-mcp — MIT, copyright Siddharth Ahuja; current package metadata names `mcp-for-blender` 2.2.4, Python >=3.10, mcp>=1.26,<2 and httpx>=.27. Third-party Blender socket/add-on bridge, not official Blender software and not a similarity optimizer. Asset-generation services are unnecessary for this workflow. Do not run its installers or change add-on/config settings automatically.

Before importing code later, pin the reviewed commit, inspect the actual source and runtime behavior, preserve its license/attribution, and separately review assets and fonts. This skill works without those repositories or MCP servers. An Illustrator server must not be called official without an Adobe-controlled source establishing it.
