# Verified delivery

Local verification: Windows, Python 3.12.4, CPU PyTorch 2.15.0, Streamlit 1.67.0. See the package lock snapshot for other versions.

## Checks executed

- **25 tests passed**: equation limits, beam-weight normalization, independent analytic wavelength-integral comparison, independent adaptive scattering-integral comparison, equation (9) energy derivative for both conventions, quadrature refinement, factorization, invalid input rejection, impossible-count disagreement, group-separated train/test splits, PyTorch checkpoint roundtrip, UI equation evaluation, real PyTorch inference, missing-model errors, surrogate/direct comparison and CSV upload.
- **Mypy passed** for the seven application/library Python files with the supplied configuration (missing third-party stubs ignored; function bodies checked).
- Editable package installation completed successfully.
- Full run completed with 120 scenarios, 360 species/setting rows, and 7,200 synthetic events. Checkpoints, numerical results, data, reports and versions are included in `example_run`.
- Classifier held-out scenario macro-F1: **0.6977**. This is not detector validation.
- Equation surrogate held-out log10 RMSE: **0.5097**; probability MAE: **0.00382027**. This approximation has meaningful error; use direct numerical results as the reference.
- The temporary localhost Streamlit server returned ready states for equation evaluation, classifier prediction, surrogate prediction and the measurement workspace. No new warnings/tracebacks appeared in its console. The upload path was exercised using Streamlit AppTest because the live agent API does not support uploads.
- Default electron conditional result at the supplied example settings: **0.0523456**; joint value **0.0150084**. The neural surrogate returned **0.0514973** for that conditional result in the live UI check.
- The prior input (5 GeV/c, 33.36 ns, 12 photoelectrons) executes the actual PyTorch classifier and is flagged as outside its training feature range. Its high softmax score is not calibrated confidence and should not be relied on as a physical inference.
- The saved scientific figure was rendered and visually checked for legibility. Proposal pages containing equations were rendered and inspected against the transcription.

## Not established

No experimental agreement, calibrated detector response, Geant4/FLUKA reproduction, real T9 beam composition, operator-theoretic derivation, or validity of the proposal's claimed benchmark numbers has been established. The proposal's dimensional and closure issues are documented, not resolved by neural-network training. No live GitHub repository was created or updated, and the supplied CI workflow has not run remotely.

This delivery is an executable, auditable starting point for testing the proposal, with explicit paths for future evidence. It is not a certificate that the equations are physically correct.
