# Equipment profiles · v0.4.0

The Live plant has an immutable built-in **Default** and up to 20 custom profiles. Profiles describe equipment, while room temperatures, ambient conditions, heat gain, thermostat/control settings, availability and playback speed remain operating settings. The reference operating-point calculator and its existing scenario format remain separate.

## Use

1. Open Live plant → Equipment profiles.
2. Choose New from Default, Duplicate, or Edit a custom profile.
3. Enter a name, notes, data source and supported specifications; Save.
4. Review the selected profile and click **Use profile**. After time has advanced the button reads **Use profile & reset plant**. This clears the run and applies the equipment while preserving operating settings.
5. Export profile JSON to share it between devices or retain a backup. Import adds a separate custom profile and never silently overwrites an existing one.

Saving changes to the active profile does not change the active equipment snapshot or current results. The new revision takes effect only on Use profile/reset. Active-profile deletion is blocked until another profile is applied. Default cannot be edited or deleted; duplicate it to customize equipment. Browser reload restores the most recently saved revision of the last active profile and starts a fresh run. No live run is restored.

## Supported specifications

- Single-stage direct expansion, with one to three identical compressors on a common header.
- Per-compressor swept displacement in m³/h, evaporator/condenser UA in kW/K, and pressure/discharge-temperature operating limits.
- Built-in example efficiency curves, or fixed volumetric, isentropic and motor efficiency assumptions in percent. Fixed assumptions affect compressor flow, work and electrical input; they do not constitute a manufacturer performance map.
- Name, description, source category/reference, immutable ID, revision, and creation/update timestamps.
- Optional receiver, evaporator and condenser volumes in m³. These are **stored-only** metadata and do not affect v0.4.0 physics. Refrigerant inventory and valve dynamics are later releases.

Data categories distinguish examples, user estimates, and user-entered manufacturer values. Manufacturer entries require a reference, but neither that label nor successful input validation establishes measured performance accuracy or an independently validated operating envelope. No manufacturer curves are downloaded or fitted in this release. Unsupported arrangements (including flooded Live plant profiles), performance-map types, schema versions, types and out-of-range values are rejected. The separate reference calculator still supports its ideal flooded mode.

## Persistence, units and exports

Profiles are stored under `ammonia-lab-equipment-v1` in browser local storage. Storage failures leave the library usable for the current session, with an explicit instruction to export JSON. Invalid stored records are skipped; a malformed/unsupported library falls back to Default without overwriting the stored data during startup. Device/browser storage is not synchronized automatically.

Profile schema `ammonia-equipment-profile`, version 1, stores pressures in bar absolute, temperature limits in Celsius, UAs in kW/K, displacement in m³/h and efficiencies in percent. The editor follows the selected Fahrenheit/Celsius and psig/absolute-pressure display units. Metadata-only edits and unit changes preserve original equipment values without display-rounding drift. JSON stays in SI, independent of display units. Imported IDs are replaced to avoid collisions; source revisions and specification provenance are retained.

Read-only equipment fields in the Live plant show the active specifications/current effective UAs. Live condenser disturbances alter effective conductance without rewriting the saved profile. Reset plant restores the active profile's baseline equipment. Applying a profile also restores its baseline equipment and limits. Live CSV begins with the active profile snapshot/revision and then explicitly labeled SI time-series columns, so an older active revision remains traceable after a newer revision is saved.

## Verification

`tests/profiles.cjs` checks Default immutability, schema/type/range rejection, revisions/import identity, damaged libraries, operating-setting isolation, unused volume fields, unchanged Default physics and applied fixed-efficiency specifications. `tests/profiles-ui.cjs` checks management controls, reset-on-application, non-disruptive saving, precise unit conversions, persistence, JSON sharing, rejected imports, deletion protection, browser storage failures and mobile layout. The existing steady/dynamic and browser regression suites also run in GitHub verification.
