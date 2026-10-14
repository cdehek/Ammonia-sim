# Physical iPad acceptance — Demo Candidate v0.1

Automated Chromium/Linux WebKit checks are desktop tests and emulation. Only the user can sign off the physical iPad, its Safari version, touch behavior and Files workflow. Record iPad model, iPadOS/Safari version, access method, date and PASS/FAIL for each item. Stop the coworker demonstration if core controls, trip evidence or export access fail.

## Obtain and open the exact candidate

- [ ] Download `ammonia-lab-demo-candidate-v0.1-20261014.html` from this release branch or extract the delivery ZIP. Its SHA256 must be `2924babd0e2c6fb37c71a9473a83f68644a154c6354a1c834513c570386f5420`. The application still reports its existing version; the filename identifies the release candidate.
- [ ] Use full Safari and confirm **Ammonia Lab / Live Plant**, charcoal/steel/green/amber styling, Fahrenheit/psig defaults and no startup notice or runtime error.
- [ ] Confirm Default equipment is active. Tap **Initialize auto DX**. Inspect all four connected vessel states, non-empty readings and schematic equipment details.
- [ ] Tap Start, watch simulated time advance, then Pause. Confirm time stops, readings remain accepted and Operator Assist says PLAYBACK PAUSED. Test 1×/10×/60× playback; pause before changing demonstrations. Compressor enabled/speed and playback pause are different controls.
- [ ] Open Plant controls, change compressor speed from 70 to 80%, observe unapplied draft, Apply, then +10 s. Confirm real readings respond. Reinitialize auto DX afterward.
- [ ] Tap compressor, condenser, receiver, evaporator, outlet and feed valve; scroll portrait schematic as needed. Try an external keyboard: focus/Enter, Operator Assist close/Escape and return focus.
- [ ] Open Operator Assist while paused and while playing. Compare suction/discharge, speed, actual superheat and valve actual/command to the HMI. Close/open without resetting time.

## Exercise, trip, history and exports

- [ ] Guided exercises → Hot condenser air → Load exercise. Read and submit the correct reflection, then apply the provided disturbance. Use its +10 s advancement until High discharge temperature trips (about 65.125 s total). Do not edit equipment limits or other inputs.
- [ ] Open Operator Assist: verify captured temperature ≈338.29 °F and modeled limit 338.00 °F; pressure ≈241.04 psig and speed 70%. Confirm the stop is an EQUIPMENT TRIP. These are model values, not real plant safety ratings.
- [ ] Trends & history: inspect the stop event and its exact triggering readings. Switch pressure/temperature/superheat/feed/level plots; pin and unpin a sample. Rotate landscape → portrait → landscape; check plot geometry, labels, cursor and scrolling, with no unintended state reset. Repeat with Reduce Motion enabled in iPad Accessibility settings.
- [ ] Use the exercise's Restore controls, Clear stop, then +10 s. Confirm objectives complete and the original stop plus clear event remain in history/export. Assist should return to paused current-state interpretation, not continue showing an active trip.
- [ ] Export exercise JSON, connected state CSV and history CSV. In Safari use the download/share action and **Save to Files**, choose an accessible folder (prefer On My iPad for offline access), then find and open/share each actual file in Files. Confirm non-empty contents, original trip evidence and SI fields. UI units should not rewrite SI evidence. Export before reload/reinitialization.
- [ ] Optional short exercise: Restricted liquid feed, correct reflection, disturbance and +10 s → completion at 40.0 s. Reset, omit reflection and advance → stopped attempt at modeled thermal trip, not a pass.

## Offline access must be demonstrated, not assumed

The bundle has no runtime Internet dependencies. That does **not** give Safari a service worker, installed PWA, or guaranteed executable local HTML in Files. Files/Quick Look can preview HTML without running the application. A previously opened HTTP page is not a dependable offline cold-start method.

- [ ] Supported Internet-independent method: put the single HTML on a laptop/local host; run `python3 -m http.server 8000 --bind 0.0.0.0` in that folder. Join the iPad and host to the same Wi-Fi/LAN and open `http://<host-LAN-IP>:8000/ammonia-lab-demo-candidate-v0.1-20261014.html` in Safari. Permit local access only as required by the host firewall. Keep the host awake. No cloud deployment is needed.
- [ ] Disconnect that LAN's Internet uplink (leave local Wi-Fi and the host connected). Close Safari's candidate tab and open the same local URL again. Initialize DX, advance, inspect Assist and export to Files. This proves cold startup without Internet, while still requiring the local host/network.
- [ ] For iPad-only offline use, test an existing trusted local HTML browser/container that actually executes the saved HTML and supports Blob downloads. Record its name/version and the exact opening/export steps. This route is not qualified by desktop `file://` tests. Do not install or assume a new app merely from this checklist.
- [ ] Airplane mode with Wi-Fi off: only claim supported if the chosen iPad-local method actually cold-starts and exports. Safari LAN access cannot work without Wi-Fi/host. If independent iPad-only offline operation is mandatory and no working method exists, acceptance is BLOCKED.

## Reset and sign-off

- [ ] Export evidence first. Pause; close Assist; select Default if changed; Initialize auto DX; restore Fahrenheit/psig and 10×; scroll to top. Confirm zero simulated seconds and no old trip in the new run. Reinitialization replaces run history, whereas restore/clear retains it.
- [ ] Open the URL with `?workspace=all` and confirm all original workspaces are available. Return to the candidate URL without that query for the next demo.
- [ ] Sign off: device/OS, exact artifact hash, method, results, defects and permission to use it for coworkers. Physical-device acceptance is pending until the user confirms it.
