# From executable equations to experimental evidence

No measurements have been supplied. The `synthetic_counts.csv` file is a same-model software check and must never be described as CERN, Geant4 or FLUKA data.

## Define what is counted before collecting data

For the comparison command, `n_incident` means the number of independently tagged **incident particles of the named species**, before applying the detection gate being tested. `n_detected` is the subset passing that predeclared gate. The code compares to P_conditional, excluding W. Do not use the total mixed-beam count as each species denominator. Do not use this project's AI classification as the independent truth label.

The printed Eq. (2) gate is an ideal photon-emission gate. PMT collection/quantum efficiency, noise, dead time, pile-up, trigger thresholds and reconstruction efficiency must be included consistently before comparison to a real readout. The current engine does not automatically calibrate those factors. Its PyTorch event generator uses a separate declared photoelectron observation layer; those generated `detected` values must not be confused with the ideal Eq. (2) quantity.

## CSV columns

| Column | Meaning |
|---|---|
| p0_MeV | Initial momentum in MeV/c, not GeV/c |
| x_cm | Proposal's shared propagation coordinate, cm |
| material | Al or Pb |
| n_ref | Constant refractive index across the configured wavelength interval |
| species | Electron, Pion or Proton |
| n_incident | Positive integer incident count of that independently tagged species |
| n_detected | Integer from 0 through n_incident |
| source_kind | experimental, reference_simulation or synthetic |
| source_id | Run/file/reference identifier; must not be blank |

All other settings come from the selected JSON configuration. Archive the complete configuration and source files for every comparison. If different rows need different stopping-power/optical/MPV tables, compare them in separate runs with the appropriate configuration. Finite beam bins require averaging predictions over the actual momentum/geometry distribution; the present row comparison treats each row's settings as fixed, not as an integrated bin.

## Suggested practical sequence

1. Resolve the equation (5) dimensions and equation (9) loss convention with a qualified physics mentor. Specify separate target/radiator/flight-path geometry and define the physical meaning of each multiplicative gate. The printed formulation is not yet a complete apparatus model.
2. Obtain material- and species-specific stopping-power/cross-section tables and measured n(lambda), absorption, detector MPV and efficiency curves. Keep calibration data separate from the later validation data.
3. Record actual beam profiles and independent species tags. Document detector resolutions, trigger logic, dead time and background subtraction. Positive/negative pion mixtures and detector response may require more species detail than this three-class prototype.
4. Collect counts at multiple momenta, target thicknesses and detector settings. Retain zero-count results, uncertainty estimates and run IDs. Preserve raw records and selection code.
5. Freeze the configuration before opening validation counts. Use the comparison command to inspect observed fractions, exact 95% intervals, expected counts, residuals and exact two-sided binomial p-values. Holm adjustment is provided for the declared set of rows.
6. Examine disagreements. Do not optimize on the validation set until the p-value looks good. If you revise/calibrate the model, evaluate it on new held-out runs and report the revision.
7. Compare against independently configured Geant4/FLUKA simulations, with versions, physics lists, geometry, cuts, seeds, uncertainties and output files archived. Reference simulation agreement supports consistency, but is not a substitute for real detector measurements.

## Interpreting statistics

The binomial test assumes independent Bernoulli trials with a fixed probability and known incident count. Systematic errors, uncertain species tags, correlated spills, background subtraction and fit-parameter uncertainty violate that simple model unless addressed separately. These are not included in the returned intervals/p-values. Use run-level analysis and an appropriate likelihood when those effects matter.

A small p-value indicates disagreement under the stated assumptions. A large p-value says the particular test did not reject the predicted probability; it does not prove the equations or demonstrate that a rival model is worse. A source_kind label records a user's provenance claim, not independent authentication of the data. The `eligible_as_independent_evidence` column means only that the row is not labeled synthetic.

The proposal's benchmark numbers have no supplied sample counts, errors or full setup definition. They cannot support a defensible chi-squared test as-is. No p-values against those bare numbers are fabricated.
