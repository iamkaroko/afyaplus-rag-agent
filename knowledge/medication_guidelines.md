# AfyaPlus Medication Guidelines

## Medication Volume Calculations

Medication volume should be calculated using the prescribed dose and the available medication concentration.

The general formula is:

volume_ml = prescribed_dose_mg / concentration_mg_per_ml

Medication calculations should use a deterministic calculation tool rather than relying only on language-model arithmetic.

## Safety

Medication calculations must not be performed when the prescribed dose or concentration is missing, zero, negative, or unclear.

The system should request clarification instead of guessing missing clinical values.

All medication calculations should clearly state the units used.
