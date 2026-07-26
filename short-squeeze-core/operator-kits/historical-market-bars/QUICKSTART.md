# Quickstart

1. **Obtain** a historical bar export you are entitled to use (see the
   provider-and-entitlement guide). The kit never fetches it for you.
2. **Place** the exact raw file under your bundle root at `raw/<your-export>.csv`
   (see the folder-placement guide). Never edit the raw file afterward.
3. **Hash** the raw file and record its SHA-256 and byte length:

   ```
   squeeze-core historical-bar-hash --file raw/<your-export>.csv
   ```

4. **Fill in** `templates/intake-manifest.template.json` and
   `templates/column-mapping-profile.template.json`. Replace every `<REPLACE: ...>`
   value and delete the `_field_guidance` blocks.
5. **Run preflight** offline:

   ```
   squeeze-core historical-bar-preflight --root <bundle-root> \
       --manifest <bundle-root>/manifest.json \
       --profile <bundle-root>/profile.json
   ```

6. **Read the status**:

   - `READY_FOR_FUTURE_ASSOCIATION` — the bundle passed the
     current checks (with the disclaimers in the preflight guide).
   - `NOT_READY_QUARANTINED` — some rows were quarantined;
     review diagnostics before relying on it.
   - `NOT_READY_REJECTED` — a barrier blocked the bundle; see
     the reason codes and the troubleshooting guide.

7. **Confirm** the export and final operator checklists.

Preflight stops before any case association. It never touches the network.
