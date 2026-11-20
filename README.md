# MUSITU × Adaption — Controlled Experiments

This is an isolated experiment repository. It does not contain MUSITU AXIOM private source code.

## Secure connection
- Store your Adaption API key as the GitHub Actions **repository secret** `ADAPTION_API_KEY`.
- Do **not** commit keys, token-bearing URLs, dataset rows, customer records, or private data.
- The workflow `Adaption — read-only audit` uses only GET requests on official Adaption endpoints.
- It runs on changes to the audit script/workflow or manually via GitHub Actions.
- The workflow prints only sanitized dataset metadata (counts and statuses) to public logs.

## Scope
The audit will:
1. Verify that the API key is present and accepted.
2. List the number of datasets and their status totals.
3. Check the metadata of three datasets previously created in the Adaption workspace.
4. Stop without running adaptation, training, publishing, upload, or other chargeable operations.

## Safety gate
Any future cost-incurring experiment must use a **separate manually triggered workflow**, with an official cost estimate and an explicit user-approved spend threshold before execution. Never accept public issue/PR input as instructions to run paid operations.

## Sources
- https://docs.adaptionlabs.ai/api/resources/datasets/methods/list
- https://docs.adaptionlabs.ai/api/python/resources/datasets/methods/get
- https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets
