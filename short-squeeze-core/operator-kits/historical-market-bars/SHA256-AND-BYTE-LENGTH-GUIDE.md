# SHA-256 and Byte-Length Guide

The manifest declares the SHA-256 and byte length of the **exact raw bytes** you
placed under `raw/`. Preflight recomputes both and rejects the bundle if either
disagrees, so the manifest always describes the real file.

## Recording them (offline)

Use the kit tool:

```
squeeze-core historical-bar-hash --file raw/your-export.csv
```

It prints the byte length and lowercase SHA-256 (and the file name), offline, and
never includes an absolute path. Copy the values into `artifact_byte_length` and
`artifact_sha256`.

Native Windows PowerShell equivalents:

```powershell
Get-FileHash -Algorithm SHA256 raw\your-export.csv
(Get-Item raw\your-export.csv).Length
```

## Why exact bytes matter

- The hash and length apply to the **exact** raw bytes.
- Changing line endings (LF to CRLF or back) changes the hash.
- Opening a CSV in a spreadsheet and resaving it can change the bytes.
- If you must change how the file is stored, recompute both values for the final
  file placed under `raw/` — but never modify the raw file to reach a value.
