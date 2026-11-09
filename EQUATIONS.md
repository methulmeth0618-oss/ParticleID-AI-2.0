# Equation-to-code audit

Source: `source/proposal.pdf`, supplied BL4S proposal, four pages. Equations (1)-(2) are on page 1, (3)-(8) on page 2, and (9) on page 3. The pages were rendered and visually checked, including the denominator in q² and the extra factor in (9).

## Conventions

Kinematic calculations use c=1: momentum in MeV/c, masses in MeV/c², energy in MeV. Lengths are cm, wavelength configuration is nm and is converted to cm, absorption coefficients are cm⁻¹, density is g/cm³, A is g/mol, and cross-section tables are millibarns (1 mb = 1e-27 cm²). hbar*c = 1.973269804e-11 MeV cm; photon energy is hc/lambda = 2*pi*hbar*c/lambda. Charge magnitude is one for the three species. TOF uses c=29.9792458 cm/ns explicitly.

The printed use of m/p and m/E is interpreted in natural units. That convention cannot by itself repair the mixed spatial dimensions in equation (5).

| Proposal equation | Python implementation | What is retained / added |
|---|---|---|
| (1), Psi | `physics.evaluate` | Scalar product W*U*R*I. Treats the normalized incoming projector's expectation as one. No operator space, noncommuting matrix representation, or density-matrix dynamics are defined by the proposal. This is a declared scalar reduction, not an implementation of an unspecified tensor operator. |
| (2), detection | `physics.evaluate` | P_joint = W*U*R*I*P_Cherenkov*D. Also reports P_conditional = U*R*I*P_Cherenkov*D for species-specific incident denominators. |
| (3), weight | `physics.weights` | E/p, normalized beam density, both mass corrections and sum over all three species. Missing w_i is closed with truncated Gaussian momentum profiles, separately configurable widths and offsets. Normalization is evaluated with normal CDFs. |
| (4), transport | `physics.evaluate` | Both momentum/acceptance terms, displacement integral and the extra scattering integral are included. beta(s) and p(s) come from the ODE. Delta p is defined as positive p0-p_exit. |
| (5), QED factor | `physics.evaluate` | Printed logarithms, threshold, species mass correction, and printed q² numeric expression. q² = Theta²*p_exit² + 13.6²*x/(X0*sigma0²). Both denominator factors are retained. |
| (6), interaction | `physics.evaluate` | Electron attenuation versus hadronic interaction branches. sigma is evaluated as a function at p_exit/(1+beta_exit); it is not multiplied by that argument. Cross sections are converted from mb to cm². A^(alpha_sh-1) is retained. |
| (7), Cherenkov | `physics.spectrum`, `physics.evaluate` | Double path/wavelength integral, exp[-mu(lambda)(x-s)], n(lambda), recoil term and threshold indicator, followed by 1-exp(-mean). The path is min(x,Lrad), as printed. No hand-set class means. |
| (8), scintillator | `physics.evaluate` | Scintillator attenuation, supplied species MPV at selected Lscint, logarithmic thickness correction, threshold and tanh response. Division grouping is explicit and selectable. |
| (9), evolution | `physics.loss_rate`, `physics.dpds`, `physics.evaluate` | Adaptive ODE with all three loss slots, the printed E/p factor and extra (1-m²/E²) factor. Missing loss functions are explicit closures rather than invented exact solutions. |

## Required closures: assumptions, not measurements

The proposal does not supply functional definitions or calibrated tables for w_i, stopping powers, sigma_hadron,i, n(lambda), mu_abs(lambda), MPV_i(L), or many detector constants. A unique numeric prediction therefore cannot be derived from the PDF alone.

`configs/proposal.json` declares a runnable example:

- p0=5000 MeV/c; x=1 cm; aluminium; sigma_xy=0.05 cm; sigma0=1 cm; epsilon=1e-6 cm.
- Beam profiles: equal Gaussian widths 100 MeV/c, zero offsets, truncated to [100,15000] MeV/c. These do not constitute a measured T9 composition. The normalized W values are unequal despite equal widths.
- Spectrum: 300-600 nm, constant n=1.0005 represented by a three-point table; zero absorption. Nonconstant tables are supported by linear interpolation.
- Lrad=5 cm, Lscint=2 cm; mu_scint=0.15 cm⁻¹, MPVs [2,3.5,4] MeV, threshold=1.5 MeV, noise=0.5 MeV. MPVs are values at the chosen thickness; changing Lscint requires updating the MPVs from calibration.
- Collision losses are constant example tables: electron 4, pion 4.5, proton 4.5 MeV/cm. **These are placeholders, not a Bethe-Bloch calculation or measured stopping powers.** They are not automatically recalibrated when switching from Al to Pb. Supply material-appropriate stopping tables before interpreting either as a physical prediction.
- Electron bremsstrahlung closure is E/X0. This is a mean-loss approximation, not a stochastic shower model. No hadron radiative-loss term is added.
- Cherenkov energy loss is computed by integrating the unattenuated emission spectrum against photon energy hc/lambda. This additional closure connects (7) to the otherwise unspecified Cherenkov loss slot in (9).
- Hadron cross sections are constant example tables at 30 mb; alpha_sh=0.71. These are **not validated pion/proton nuclear cross sections**. Interpolation uses endpoint values outside table axes; extend tables to cover your data rather than relying on that behavior.
- Lambda_QCD=200 MeV and QED threshold=10 MeV. These are explicit inherited example scales, not fitted measurements.

Material rho, A and X0 come from PDG's [aluminium table](https://pdg.lbl.gov/2021/AtomicNuclearProperties/HTML/aluminum_Al.html) and [lead table](https://pdg.lbl.gov/2021/AtomicNuclearProperties/HTML/lead_Pb.html). This sourcing does not validate the proposed combinations of material constants. Consult [PDG Passage of Particles Through Matter](https://pdgweb.lbl.gov/2024/reviews/rpp2024-rev-passage-particles-matter.pdf) for established transport and energy-loss methods.

## Dimensional and physical issues to resolve

### Equation (5): q² is not dimensionally consistent as printed

The integral defining Theta contains (x-s)² times a dimensionless angular variance. Theta therefore has dimensions of **length**, not angle. Theta²*p² has dimensions cm² MeV² under the declared convention. The second term 13.6²*x/(X0*sigma0²) has dimensions MeV²/cm². Neither can be added to the other or inserted into a logarithm divided by a mass squared without additional definitions/scales.

`printed_cm` keeps the printed numerical arithmetic in the declared cm/MeV convention so it can be inspected. It is explicitly not unit-invariant physical q². The alternative `angular_diagnostic` uses the unweighted angular-scattering integral times p_exit² plus 13.6²*x/X0. That has MeV² dimensions, but **is a proposed diagnostic modification, not the proposal's original expression or a validated QED derivation**. Both results are exported in `equation_variants.csv`.

### Equation (9): energy-momentum consistency

For E²=p²+m², dE/dp=p/E. If S is the bracketed positive energy loss per unit distance, then dE/ds=-S requires dp/ds=-(E/p)S. The printed equation instead multiplies this by (1-m²/E²)=beta², giving dE/ds=-beta²*S. These differ for massive particles, especially at lower momentum. Unless S is defined differently from conventional stopping power, this is a physical inconsistency.

`evolution='proposal'` retains that beta². `evolution='kinematic'` removes it, as a separately labeled comparison. Tests verify both derivatives against the relativistic identity. Neither choice validates the supplied S tables.

### Equation (8): inline division grouping

The PDF uses an inline slash without an enclosing numerator around the full threshold difference. The usual dimensionless threshold argument is `(MPV_corrected - E_threshold)/E_noise`; this is the explicitly declared default `difference_over_noise`. The literal operator-precedence reading is `MPV_corrected - E_threshold/E_noise`; it subtracts unlike dimensions. `literal_slash` is provided only for numerical comparison, not silently treated as a physical correction. The prior Python code used the grouped difference.

### Geometry and detector interpretation

The same x and p(s) are used for solid-target transport and Cherenkov emission, because the PDF does not specify separate coordinate maps or media segments. A solid Al/Pb target plus a downstream gas counter is **not physically equivalent to this shared-coordinate realization**. A practical beamline model must introduce and validate separate target, flight and radiator segments. This is left explicit rather than disguised with fabricated geometry.

Equation (7) is a photon-emission probability with ideal photon counting. It does not include collection efficiency or PMT quantum efficiency. The PyTorch event generator adds 15% photon-to-photoelectron efficiency, Poisson counting, 1% lognormal momentum resolution and 0.08 ns TOF noise over a downstream 10 m flight path. These are supplemental assumptions. Its `detected` column uses the observed NPE>0 gate and the other U*R*I*D factors, so its detection efficiency differs from the ideal Eq. (2) photon gate. It must not be substituted for Eq. (2) count validation without accounting for this change.

Hadronic I is an interaction probability while electron I is an attenuation factor. The interpretation of detection after hadronic branching must be justified; no secondary-particle transport is simulated. Multiplying scalar factors assumes an appropriate factorization that also requires validation.

## Numerical safeguards and scope

- ODE rtol=1e-8, atol=1e-8, maximum step=x/20. Evaluation stops with an error if momentum falls to 1 MeV/c; it does not extrapolate a through-going model past stopping.
- Gaussian quadrature with 64 points by default, 128-point comparisons in reports. Scattering uses s=x*t^4 to resolve the logarithmic endpoint. Convergence at one configuration does not establish convergence everywhere; refine near thresholds.
- No clipping of negative recoil kernels or out-of-range final probabilities to make plots look physical. Results retain flags; event generation/count comparison rejects invalid probabilities.
- x=0 is excluded because the printed QED logarithm is undefined there. Boundary limiting behavior is not invented.
- A finite value in [0,1] is a **range check**, not physical validation.
- The paper's stated Geant4/FLUKA comparison and quoted benchmarks cannot be verified without the referenced files, configurations, sample counts and uncertainties. They are not promoted to ground truth.

## Comparison with your original Python script

| Component | Original script | This rebuild |
|---|---|---|
| W | Omitted the beam-profile density ratio | Includes configurable normalized momentum profiles |
| Transport | Constant momentum; omitted the separate angular integral in the exponent | Evolving p(s), beta(s), displacement integral and extra angular integral |
| q² | Used only 13.6²*x/X0 | Printed two-term numeric expression, plus a labeled dimensionally modified diagnostic |
| Hadronic branch | Cross-section value 0.03 without declared conversion; saturation | mb→cm² conversion and configurable sigma(argument) tables; no saturation forced |
| Cherenkov | Constant n, ad hoc light-yield factor 0.05*Lrad | Wavelength/path integral, absorption, recoil and threshold from (7) |
| Scintillator | Invented mass-power MPVs | Explicit supplied MPV values and documented grouping alternatives |
| Evolution | No equation (9) integration | Adaptive ODE and independent kinematic comparison |
| Monte Carlo | Manually chosen detection means 0.35/0.20/0.10 | Equation photon mean and explicit measurement noise; synthetic count closure test |
| Optimization | n_ref did not reach the Cherenkov calculation | n(lambda) enters the spectral calculation; no fit to unverified target benchmarks |
| AI | Separate toy Random Forest extension | Actual PyTorch classifier and equation surrogate using the rebuilt pipeline |

Default old/new outputs should not be interpreted as a controlled experimental comparison: the old script used different x, n and acceptance assumptions. The audit explains the structural differences instead of pretending those defaults represent the same apparatus.
