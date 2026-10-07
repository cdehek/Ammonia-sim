# Property provenance

The offline grid was generated with CoolProp 7.2.0, HEOS::Ammonia. It contains 241 logarithmically spaced pressure rows, 126 superheat points per row, and 31 subcooling points per row. Liquid points below −73.15 °C are marked unavailable. Saturation properties, h and s are linearly interpolated; density is interpolated logarithmically. No external fluid library runs inside the browser.

Equation of state: Gao, K.; Wu, J.; Bell, I. H.; Lemmon, E. W. (2020), Thermodynamic Properties of Ammonia for Temperatures from the Melting Line to 725 K and Pressures to 1000 MPa. See https://coolprop.org/fluid_properties/fluids/Ammonia.html .

CoolProp project and license: https://github.com/CoolProp/CoolProp (MIT license). Native CoolProp binaries are not included in the application/source archive. Generated values retain the default CoolProp h/s reference; energy and entropy differences are what the cycle uses.

Independent check: Danfoss fact sheet AM187286420404en-000702, May 2025. R717 controller-fit constants A1=10.760, A2=−2307.3, A3=247.9, Te=A2/(ln(P/bar)−A1)−A3. This is an approximate controller correlation derived from REFPROP 10; agreement does not establish independent measured-property accuracy.

Seeded verification cases were generated at states not tied to the browser grid. The maximum observed numerical errors are recorded in validation.json and displayed in the app. No claim of experimental plant validation is made.
