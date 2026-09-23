# Italic API documentation

The public documentation for the Italic recording API, hosted on Mintlify Starter:
https://italic.mintlify.site
This repository contains documentation only. App source and account data remain
in their own systems.

Mintlify configuration: repository `ShopItalic/docs`, branch `main`, documentation
directory `/` (repository root). Git pushes automatically publish the site after
the Mintlify GitHub App is installed for this repository.

Brand colors and the wordmark come from the shared Italic design tokens and
`ShopItalic/store/public/logos/italic.svg`. `docs.json` sets the light and dark
logos, the curved-S favicon, and the site colors.

## Keeping the reference current

`openapi.json` is the contract served by the production API at
https://app.italic.com/api/v1/openapi.json. The **Sync live API reference** workflow
checks it hourly and can also be run manually after an API deployment. It validates
the response and commits only when the contract changes, triggering Mintlify.
Failed requests or invalid responses leave the published reference intact.
GitHub scheduled jobs can be delayed; a manual run is available for immediate
release verification.

Edit the MDX guides directly and push to `main` to publish them. Guide prose is
maintained alongside API changes; it is not rewritten automatically.

## Local development

Install the official Mintlify CLI, then run `mint dev` in this directory.
Use `mint validate` to validate the site, and `python3 scripts/sync-openapi.py`
to refresh the reference from the live API.
