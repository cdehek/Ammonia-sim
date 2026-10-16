# 🔧 Ammonia Lab — The Mechanic’s Report

The vapor calculation was finishing one move ahead of its instruments. The
density solver took its final step, but pressure and energy could still be read
from the previous density. Each number looked plausible; together they described
two slightly different ammonia states.

The repair makes the existing backend commit its final density and temperature
through the normal state-update operation. That refreshes the instruments at
the coordinates actually returned. No ammonia equations, requested inputs or
refrigeration-solver tolerances were changed.

The original failure was reproduced first, including the exact recorded density
step. After repair, the saved vapor's pressure, enthalpy and internal energy agree
with independent EOS evaluation at its returned coordinates. Its energy mismatch
falls from roughly eight times the accepted local limit to well below that limit.
The earlier liquid repair and 44-bit precision improvement still work.

Native Linux, Chromium and desktop WebKit pass the focused checks. The accepted
five-section model completes the selected startup, disturbance, reversal and
liquid/vapor zero-exchange trials. The extra state refresh costs roughly 11–14%
on the measured vapor PT workload; observed WASM memory does not increase.

The upper-quality classification fault and 35-bar recovery/support problems
remain separate jobs. A browser research-loader exception issue also remains
visible when PT rejects an almost-saturated state. Full qualification and real
iPad testing are still pending.

The repaired parts, control parts, measurements and instructions are preserved
on the B4B research branch. The next step is engineering review and explicit
approval. Production and Live Plant remain unchanged.
