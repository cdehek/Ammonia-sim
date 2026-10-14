# Physical iPad review gate

Not yet performed. Playwright screenshots and touch emulation are not physical iPad validation. Record iPad model, iPadOS/Safari version, browser zoom, orientation and keyboard type before testing. Use the feature-branch standalone artifact; do not replace the existing Cloudflare preview.

- Open in landscape. Confirm the schematic is the main workspace, all six readings are legible, and the console launcher is easy to reach.
- Tap Open, Expand, Partial height, Collapse and Close. Confirm every button is usable by touch and the playback header remains accessible when expanded.
- With the partial console open, inspect both rows of equipment by scrolling the schematic. Check horizontal inspection in portrait without shrinking the whole drawing.
- Move between all console tools. Confirm current settings, accepted time, trend selection and retained attempts survive navigation.
- Select Hot Condenser Air, load Default equipment if necessary, and allow the automatic warmup. Find the explanation, next action, reflection and hint without searching the whole page.
- Perform the established disturbance, advance time, inspect the actual trip in Operator Assist, restore off-state controls, clear the modeled stop and advance the required 10 seconds. Check recorded objectives and export the attempt.
- Repeat the other four exercises. Try a supported disturbance-before-reflection order; guidance must not impose a new requirement.
- Check that Operator Assist keeps its recorded trip reason and values after tool changes, collapse/reopen, rotation and display-unit conversion.
- Rotate while an exercise is active. Check the console tabs, reflection select, profile fields, charts and export buttons for clipping or unwanted page overflow.
- Focus number fields with the onscreen keyboard. Confirm the focused field and apply action can be reached, the console scrolls internally and closing the keyboard restores usable geometry.
- With a hardware keyboard, use Tab, Shift+Tab, Enter, Space and Escape. Confirm focus returns to the correct launcher and navigation is not trapped. Check VoiceOver headings, selected-tool indication and status announcements.
- Enable Reduce Motion. Confirm there is no required gesture or distracting panel animation.
- Test local/offline loading through the intended iPad file workflow. The Linux WebKit `file://` finding does not establish iPad Files/Safari behavior.
- Review the unresolved WebKit playback/pause and chart-resize findings on the real device. Do not dismiss them solely because step-based workflows and evidence comparisons pass.

Record findings and screenshots, then decide whether further UI changes or WebKit investigation are needed. This branch stops for that review; it does not authorize a merge, release or deployment.
