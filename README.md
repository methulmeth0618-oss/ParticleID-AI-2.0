# ParticleID proposal lab — PyTorch rebuild

This is a fresh Python project built around the nine equations in your supplied BL4S proposal. It evaluates their numerical consequences, makes missing inputs explicit, trains actual PyTorch models on equation-derived synthetic data, and prepares comparisons against future independent measurements.

**It does not claim to prove the proposal correct.** There are unresolved dimensional/physical issues in the printed equations and no experimental or reference-simulation data have been supplied. The project can expose disagreement as well as agreement.

Your previous project is retained separately. Inside this rebuild, `source/proposal.pdf` and `source/original_simulation.py` preserve the proposal and original code. The new implementation does not import the old Random Forest model or its hardcoded histogram centers.

## Start on Windows

Extract this ZIP into a new folder. Open PowerShell inside the extracted folder:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[ui,dev]"
.\.venv\Scripts\python -m streamlit run app.py
```

Open the local URL shown by Streamlit. You can use the bundled trained models immediately; no retraining is required to inspect the example. Python 3.11+ is required; Python 3.12 is the tested environment. CPU PyTorch is sufficient. If your package mirror has an older Streamlit, use the documented version-compatible environment rather than removing unsupported arguments blindly.

## The three workspaces

1. **Equations:** enter beam momentum, x, material and refractive index. Inspect W, U, R, I, Cherenkov and scintillator factors, conditional/joint values and momentum trajectories. Switch the separately labeled equation variants to see their effects.
2. **PyTorch prediction:** classify an event from measured downstream momentum, TOF and photoelectron count, or compare a neural equation surrogate with direct numerical evaluation. Your prior inputs 5.0 GeV/c, 33.36 ns and 12 photoelectrons are prefilled. Extrapolation is flagged. The new model can disagree with the old toy-trained model.
3. **Measurement comparison:** upload species-specific incident/detected counts with provenance. Compare against fixed-parameter conditional predictions, exact binomial intervals/tests and Holm-adjusted p-values.

## Reproduce the supplied run

```powershell
.\.venv\Scripts\proposal-pid run --config configs/proposal.json --output runs/demo
.\.venv\Scripts\proposal-pid predict --model runs/demo/classifier.pt --momentum 5.0 --tof 33.36 --photoelectrons 12
.\.venv\Scripts\python -m pytest -q
```

After retraining, enter `runs/demo` in the interface's model-folder field. Existing output folders are rejected so previous results are not overwritten. Use another folder name for the next run. A quick development run can use `--scenarios 20 --events-per-species 5 --epochs 20`; it is not the delivered training configuration.

To calculate equations without training:

```powershell
.\.venv\Scripts\proposal-pid evaluate --config configs/proposal.json --output runs/equations
```

To compare future counts:

```powershell
.\.venv\Scripts\proposal-pid compare --config configs/proposal.json --input measurements.csv --output runs/measurement-comparison
```

Use `templates/measurements.csv` and read [MEASUREMENTS.md](MEASUREMENTS.md). Empty templates contain no fabricated observations.

## How the equations connect to PyTorch

The engine solves equation (9), then uses p(s) and beta(s) in the transport and spectral integrals. It produces every operator factor and the scalar product in (2). Those values drive the synthetic dataset and the surrogate targets.

- **Classifier:** a 3→48→48→3 neural network with ReLU layers, trained with cross-entropy and Adam. Inputs are measured downstream momentum, TOF residual relative to a 10 m light-speed flight, and log(1+photoelectrons). It does not use true species, simulation scenario ID, hidden true mass, detection label or equation-derived species probabilities as input features.
- **Equation surrogate:** a 6→48→48→1 network trained on log10(P_conditional), with a 1e-12 floor for zeros. Inputs are initial momentum, x, refractive index and a species one-hot vector. It approximates the numerical equations, not nature. The example fixes n=1.0005 and aluminium: a different n/material/closure configuration requires new training; the model does not learn material effects from a fixed-material run.
- Scenarios are split 60/20/20; all species/events from one scenario stay together. Normalization is fitted on training rows only. Validation selects the checkpoint; held-out test scenarios are not used for fitting. PyTorch state dictionaries and scaling metadata are saved in `.pt`, loaded with `weights_only=True` and `model.eval()`.
- The classifier uses balanced incident species, not measured beam fractions or Eq. (3)'s weights. Its softmax scores are uncalibrated and depend on that sampling. A real mixed-beam prior requires validation/calibration.

## Inspect these first

- [EQUATIONS.md](EQUATIONS.md): equation-by-equation mapping, units, closures and issues.
- [example_run/REPORT.md](example_run/REPORT.md): actual numerical and training results.
- [MEASUREMENTS.md](MEASUREMENTS.md): experimental validation plan and CSV definition.
- [VALIDATION.md](VALIDATION.md): what was tested and what remains unvalidated.
- `configs/proposal.json`: every supplied example input; change these with calibrated values.

The delivered default run uses 120 scenarios and 7,200 synthetic events. All numeric scores in the report come from execution. The classifier macro-F1 is about 0.698; the surrogate log10 RMSE is about 0.510, so the surrogate can have substantial multiplicative error. Always use direct equation evaluation for the theoretical reference.

## Important change from the first project

The old hand-picked Gaussian detection histograms and benchmark-fitting optimization are removed from the new workflow. The new histogram/data values arise from explicit equations and measurement assumptions. The PyTorch models replace the earlier Random Forest. All numerical/physical caveats are retained in the output files; the code does not tune constants to force the proposal's 0.0048/0.0001 claims.

## GitHub and reproducibility

The repository layout includes tests, a GitHub Actions workflow and `.gitignore`. It has not been published. No license is assigned to your original proposal/code. Choose one before distributing for reuse. `requirements-tested.txt` records the local package versions; `example_run/environment.json` records numerical-library versions, and SHA256SUMS files identify the delivered files.

On Linux/macOS, replace `.venv\Scripts\python` with `.venv/bin/python` and the executable paths likewise. Only the local Windows/Python 3.12 execution is verified here; GitHub CI is supplied but not remotely executed.

Primary implementation references: [PDG material properties](https://pdg.lbl.gov/2023/AtomicNuclearProperties/), [PDG particle passage review](https://pdgweb.lbl.gov/2024/reviews/rpp2024-rev-passage-particles-matter.pdf), [PyTorch checkpoint guidance](https://docs.pytorch.org/tutorials/beginner/saving_loading_models.html). The proposal remains the source of equations (1)-(9); these references do not endorse those equations.
