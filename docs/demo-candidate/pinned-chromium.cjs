// Select the Chromium revision shipped with pinned Playwright 1.62.1.
// Existing helper otherwise selects the host's unrelated /usr/bin/chromium.
// All test code, clocks, actions and assertions remain unchanged.
const {chromium}=require('playwright'),launch=chromium.launch.bind(chromium);
chromium.launch=options=>{const copy={...options};delete copy.executablePath;return launch(copy);};
