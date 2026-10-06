# Security Policy

## Supported Versions

Currently, the Smart RMS prototype is supported strictly as a non-production academic demonstration. 
The current version `1.0.0` is the only supported version.

## Synthetic Data Policy
The Smart RMS project is explicitly engineered to process **synthetic data only**. 
Under no circumstances should this repository or its instances connect to live LPU production databases or contain genuine student PII (Personally Identifiable Information). All testing, benchmarking, and ML evaluation MUST use the provided synthetic benchmark datasets.

## Vulnerability Reporting Guidance
If you discover a potential vulnerability within the Smart RMS architecture (e.g. prompt injection, PII redaction leakage, or RBAC bypassing):

1. **Do not disclose the issue publicly** on GitHub.
2. Please send a detailed report via private communication to the academic maintainers of the project.
3. Include the exact reproduction steps, impact assessment, and potential mitigations.

## Secrets Policy
- API Keys, passwords, and sensitive credentials MUST NEVER be committed to the repository.
- Use the `.env.example` file to template your environment variables.
- Maintainers must run a secret scanning tool before merging branches into `main`.

## Authentication & Role-Based Access Control (RBAC) Expectations
- Actions related to **Model Governance** (promoting/rolling back models, verifying offline challengers) are strictly restricted to `ML_ADMIN` or `ADMIN` roles.
- Standard staff (`STAFF`, `SUPERVISOR`) should only interact with operational routes (Draft approval, intent correction).
