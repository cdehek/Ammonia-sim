# Live Plant Focus Mode

This milestone changes application presentation only. Live Plant opens immediately, with the approved HMI, all seven section links, Operator Assist v0.1, unit selectors and simulated-time controls. The independent reference calculator and its exports are retained but hidden along with the old top-level navigation.

## Restore the retained workspaces

For one session, append `?workspace=all` to the HTML URL (or `&workspace=all` when another query parameter is present). This works with local/offline HTML and HTTP. The original six tabs and reference controls return, starting at Cycle Overview. Remove that parameter to return to Live Plant Focus Mode. No storage setting, network service or module deletion is involved.

For a persistent build change, set `DEFAULT_WORKSPACE` in `app.js` from `'live'` to `'all'`, then run `npm run build`. `?workspace=live` overrides that setting for a focus-mode session. This switch only selects the initial workspace and visibility; all models, event handlers, data and exports remain loaded.

## Scientific information

**Model information / limitations** provides the illustrative-model, uncalibrated-equipment and real-plant-accuracy limitations, including the prohibition on using the simulator for actual plant safety decisions. **View existing model & validation details** opens the original validation workspace and its embedded reports. **Return to Live Plant** returns focus to the limitations entry without resetting a run or changing any data.

## Verification

`npm run test:browser` includes the focus-mode suite and all retained browser suites. Legacy tests that exercise top-level navigation explicitly use `?workspace=all`; Live Plant preservation tests open the default focus workspace and retain their original scientific assertions. `npm run test:webkit` includes the new focus suite and the repository's existing WebKit selection. `npm test` remains unchanged.

See [The Mechanic's Report](MECHANICS_REPORT.md) for results, review evidence and exact changed files.
