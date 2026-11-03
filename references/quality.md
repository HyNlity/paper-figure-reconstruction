# Comparisons and acceptance

Read source pixel dimensions and transparency before analysis. Inspect the full image composited on white and enlarge ambiguous regions; a dark transparency preview may hide black labels. Preserve the source aspect ratio. Do not stretch a reference to an accidentally chosen canvas merely to make a comparison run.

Compare identical canvas dimensions, compositing transparency over the same declared background (white by default). Refuse silent resizing. Record PDF crop and any explicit coordinate conversion. Do not use nonrigid registration to conceal geometry errors.

The helper computes RGB MAE and local grayscale SSIM: 11x11 uniform window, population covariance, K1=.01, K2=.03, data range 1, valid interior. It is not Gaussian-window scikit-image SSIM; report the variant. For crops smaller than 11 pixels use the largest odd fitting window. Contours are luminance gradient pixels above 0.08; symmetric nearest contour distance is reported in pixels using bounded NumPy blocks (mean and 95th percentile). Missing contour on only one side is a failure (`null` distance plus explicit status), not zero error. Report full canvas and each panel/ROI. Metrics are diagnostics, not a scientific correctness certificate or a percentage of perfect reconstruction.

Scientific meaning takes precedence over polished materials or similarity scores. Resolve ambiguous material identity, lattice topology and the meaning of repeated motifs before constructing that detail. Check that apparent arrows, bonds, atoms or material layers have not been substituted for one another. A confirmed generic “2D material” does not identify its crystal structure.

Look for missing/extra elements, occlusion order, endpoints, repeated atom topology, silhouette landmarks, handedness, glyphs and color/alpha artifacts. Add landmark errors when trustworthy landmark pairs are available; do not report a small landmark residual as whole-image accuracy. White backgrounds can dominate SSIM, so inspect foreground and panel crops. Report raw comparisons; record any aligned diagnostic separately.

Test metric behavior using identical images, known translation, a missing arrow and changed text. Actual editability tests modify disposable SVG/AI label and path objects and Blender geometry, reopen/save/rerender, and check intended changes. Validate source rebuilds in relocated directories. Protected panels require pixel comparisons and/or geometry/material snapshots; object counts alone are insufficient.

Quality report: reference/provenance, software versions, representation/editability inventory, per-iteration change and metric table, semantic checklist with evidence/uncertainties, protected-region checks, failed/unexecuted checks, residual deviations and deliverable paths. Never claim 1:1 based on a single score. Keep paper reference assets local unless their redistribution rights have been established.

## Case: twisted material stack with optical fields
The first attempt constructed slab meshes from individually guessed screenshot corners and drew beams and polarization motifs in SVG. It did not export each slab separately, but it still lacked a coherent 3D construction and misidentified the slab outline. Material work and export checks came before resolving the main geometry.

The revised approach recognized hexagonal thin prisms, instantiated a shared unit along an optical axis, rotated the units about that axis, and modeled beams, helices and field spokes in the same Blender scene. Shared projection and occlusion improved the overall construction and appearance. This is a method improvement, not a completed faithful-reconstruction claim: ambiguous internal motifs were still modeled as arrow-like triangular protrusions rather than correctly representing the 2D material. The user identified that remaining error. The appropriate next step is to ask about the material/structure, not add more invented detail or rely on a schematic disclaimer.

Do not turn this example's estimated dimensions, number of slabs, twist angles or material motifs into defaults for other figures. Retain its decision rule: confirm scientific identity, establish coherent geometry, inspect the unlabelled composition, then refine supported detail and add annotations.
