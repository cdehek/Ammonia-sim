# Equipment profiles · v0.4.5

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
- Receiver, evaporator and condenser refrigerant volumes in m³, with optional saturated inventory initialization by liquid volume fills or total modeled charge. The preview uses real-fluid densities, but these settings do not affect the original quasi-steady room physics. The separate storage laboratory uses these settings; optional connection specifications enable stage-3 circulation.

Data categories distinguish examples, user estimates, and user-entered manufacturer values. Manufacturer entries require a reference, but neither that label nor successful input validation establishes measured performance accuracy or an independently validated operating envelope. No manufacturer curves are downloaded or fitted in this release. Unsupported arrangements (including flooded Live plant profiles), performance-map types, schema versions, types and out-of-range values are rejected. The separate reference calculator still supports its ideal flooded mode.

## Persistence, units and exports

Profiles are stored under `ammonia-lab-equipment-v1` in browser local storage. Storage failures leave the library usable for the current session, with an explicit instruction to export JSON. Invalid stored records are skipped; a malformed/unsupported library falls back to Default without overwriting the stored data during startup. Device/browser storage is not synchronized automatically.

Profile schema `ammonia-equipment-profile`, version 3, stores pressures in bar absolute, temperature limits in Celsius, UAs in kW/K, displacement in m³/h and efficiencies in percent. The editor follows the selected Fahrenheit/Celsius and psig/absolute-pressure display units. Metadata-only edits and unit changes preserve original equipment values without display-rounding drift. JSON stays in SI, independent of display units. Imported IDs are replaced to avoid collisions; source revisions and specification provenance are retained.

Read-only equipment fields in the Live plant show the active specifications/current effective UAs. Live condenser disturbances alter effective conductance without rewriting the saved profile. Reset plant restores the active profile's baseline equipment. Applying a profile also restores its baseline equipment and limits. Live CSV begins with the active profile snapshot/revision and then explicitly labeled SI time-series columns, so an older active revision remains traceable after a newer revision is saved.

## Verification

`tests/profiles.cjs` checks Default immutability, schema/type/range rejection, revisions/import identity, damaged libraries, operating-setting isolation, unused volume fields, unchanged Default physics and applied fixed-efficiency specifications. `tests/profiles-ui.cjs` checks management controls, reset-on-application, non-disruptive saving, precise unit conversions, persistence, JSON sharing, rejected imports, deletion protection, browser storage failures and mobile layout. The existing steady/dynamic and browser regression suites also run in GitHub verification.

## Starting inventory · stage 1

Default supplies illustrative volumes (receiver 0.25 m³, evaporator 0.08 m³, condenser 0.12 m³), initial pressures (2.5 and 12 bar absolute), and liquid volume fractions (30%, 10%, 10%). These are independent example assumptions, not a measured charge or a demonstrated match to Default equipment capacity.

Choose **Not configured** to keep initialization optional, including incomplete volume metadata. Choose **Liquid fills** to calculate charge from all three fills. Choose **Total charge** to specify modeled ammonia mass in kg and calculate receiver fill while retaining evaporator/condenser fills. Switching between configured fill and charge modes seeds the calculated input to preserve the starting inventory. The calculated variable is stored as null: `chargeKg` in fills mode, receiver fraction in charge mode. Entering both is rejected, preventing an overdetermined initial state. All three positive volumes and explicit initial pressures are required when initialization is enabled.

`inventory.volumes` holds m³ or null; `inventory.initialization` is null or `{mode, chargeKg, suctionPressure, dischargePressure, liquidFractions}`. Pressures are bar absolute, mass kg, fractions 0–1 by **liquid volume**, independent of vapor mass quality. The editor displays pressure in the selected units and fractions in percent. Untouched values survive unit changes and metadata edits without rounding drift. Initial pressure is separate from the operating suction setpoint.

Receiver and condenser initialize at discharge-side saturation pressure; evaporator at suction-side saturation pressure. The preview calculates each vessel's liquid/vapor mass, total mass, vapor mass fraction, saturation temperature and internal energy from the embedded property grid. Charge mode rejects values outside the receiver's vapor-only to liquid-only mass capacity, with other fills fixed. Endpoint fills are accepted and flagged as phase-boundary cases for stage 2. This checks initialization feasibility; it does not certify a real equipment operating envelope or allowable receiver fill.

The three isolated, fixed refrigerant volumes exclude connected piping, compressor/valve holdup, metal thermal energy, oil and noncondensables. Startup is not assumed to be a connected-system steady equilibrium. See [INVENTORY_INITIALIZATION.md](INVENTORY_INITIALIZATION.md) for the initialization contract; connected outlet partitioning is described in VALVE_CONTROL.md.

## Migration

Version-1 profiles are accepted and normalized into version 3 without changing equipment, ID, revision or dates. `futureVolumes` becomes `inventory.volumes`; initialization becomes null, because charge and pressures cannot be inferred from old data. No missing volumes are replaced with zero or Default guesses. Migration occurs in memory on load; saving/importing/applying persists a version-3 library under the existing storage key. No old run is restored. Export a backup before using older app versions: version-3 exports/libraries require stage 3 or newer; version-1 and version-2 exports remain importable. Invalid records continue to be skipped individually.

Profile exports, duplication, revisions, reload and active-profile CSV snapshots include the new initialization specification. Saving a new revision remains non-disruptive. Neither `inventory` nor initialization-derived mass/energy is passed into the original quasi-steady live engine. The stage-2 storage laboratory initializes a separate conserved inventory from the active snapshot and requires a ready initialization.

## Version 3 connections

A nullable `connections` object holds effective feed/drain/vapor areas (Cd × A, m²), pressure recovery factors, the opening exponent, actuator/sensor time constants (s), condenser-to-receiver elevation head (m), outlet fractions of the existing evaporator volume/UA, and initial outlet superheat (K). Bounds are centralized in `connectionBounds` and enforced on edits, imports and restore. Default is revision 3 with illustrative connections. Older v1/v2 records migrate with `connections: null`; existing charge, equipment, identifiers and revisions are preserved. Their closed-storage behavior is retained. Explicitly enable and configure connections in a custom profile to use circulation. Operating mode, target, PI gains, speed and commands stay outside profiles. See [VALVE_CONTROL.md](VALVE_CONTROL.md).
