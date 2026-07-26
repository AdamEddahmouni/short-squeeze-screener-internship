# Folder Placement Guide

Lay a bundle out like this:

```
<bundle-root>/
  manifest.json      # your filled-in intake manifest
  profile.json       # your filled-in column-mapping profile
  raw/
    <your-export>.csv # the exact raw file, never modified
```

- `artifact_relative_path` in the manifest points at the raw file **relative** to
  the bundle root, e.g. `raw/your-export.csv`. It must never be an absolute path
  and must never escape the root with `..`; absolute/machine paths never enter any
  deterministic identity.
- Keep the raw file exactly as obtained. The workflow never rewrites it.
- Regenerated canonical outputs (normalized bars, diagnostics, the preflight
  report) are written separately and never overwrite the raw file.

## Private intake root

If you place bundles under the repository's private intake root
(`intake/local-bars/`), that path is git-ignored so a real licensed export is
never committed. Never commit a real export unless you have explicitly authorized
that exact file.
