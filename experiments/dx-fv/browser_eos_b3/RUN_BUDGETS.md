# B3 execution bounds

The focused matrix has 57 base PH inputs: the saved vapor fixture, 24 preserved
B2 boundary inputs (0, .001 and .01 J/kg outward from each endpoint at four
pressures), and 32 labeled diagnostic quality-offset inputs on both sides of
each endpoint, at +/-0.99e-9 and +/-1.01e-9 times latent enthalpy. None replaces a
solver finite difference. Every browser base retains the four original signed
P/h probes: 285 snapshots per build/engine, 2,280 total. Physical phase crossings
and unsupported pressure probes have explicit derivative exclusions.

Unmodified native initial compilation: 900 seconds. Subsequent compilation per
historical precision/logging variant: 600 seconds. Native measurement process:
120 seconds; independent browser audit: 180 seconds; browser campaign: 600
seconds, launch/navigation: 30 seconds. The sequential native build campaign
has an additional 1,500-second wall cap. Downloads use explicit timeouts where
supported. Outputs are additive and existing evidence files refuse overwrite.

No complete B2 or A2 qualification campaign, operating trajectory or endurance
test runs in B3. Setup failures and partial/failed scientific results remain
visible. There is no success conversion for a backend or guard exception.
