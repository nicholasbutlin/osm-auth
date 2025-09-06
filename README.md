# SCOUTING-ACCOUNTING

```
                          __  _
   ______________  __  __/ /_(_)___  ____ _      ____ _______________  __  __
  / ___/ ___/ __ \/ / / / __/ / __ \/ __ `/_____/ __ `/ ___/ ___/ __ \/ / / /
 (__  ) /__/ /_/ / /_/ / /_/ / / / / /_/ /_____/ /_/ / /__/ /__/ /_/ / /_/ /
/____/\___/\____/\__,_/\__/_/_/ /_/\__, /      \__,_/\___/\___/\____/\__,_/
                                  /____/
          __  _
   ____  / /_(_)___  ____ _
  / __ \/ __/ / __ \/ __ `/
 / / / / /_/ / / / / /_/ /
/_/ /_/\__/_/_/ /_/\__, /
                  /____/
```

## Table of Contents

- [SCOUTING-ACCOUNTING](#scouting-accounting)
  - [Table of Contents](#table-of-contents)
  - [About The Project](#about-the-project)
  - [System Overview](#system-overview)
  - [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
  - [Usage](#usage)
    - [Running the Application](#running-the-application)
  - [Integrations](#integrations)
    - [Xero](#xero)
    - [GoCardless](#gocardless)
    - [SumUp](#sumup)
  - [Development](#development)
    - [Version Control](#version-control)
    - [Release](#release)
  - [License](#license)

## About The Project

Scouting-Accounting is a tool designed to help scout groups manage their financial accounts by integrating with various payment platforms and accounting systems. The application facilitates the collection, processing, and reconciliation of financial transactions from multiple sources.

## System Overview

The application integrates with three main payment/accounting systems:

- **Xero**: Accounting software integration
- **GoCardless**: Direct debit payment platform
- **SumUp**: Card payment processing service
- **OSM**: Online Scout Manager
- **Stripe**: Payment processing platform - PLANNED

Data from these systems is fetched, normalized, and can be used for reporting and reconciliation purposes.

## Getting Started

To get a local copy up and running follow these simple steps.

### Prerequisites

In order to be able to install, run and develop with this application you need:

1. Git - so the repo can be cloned
2. Python >= 3.10
3. [Pipenv](https://pipenv.pypa.io/en/latest/) for virtual environment and dependency management
4. API credentials for the integrated services (Xero, GoCardless, SumUp)

### Installation

1. Clone the repo and cd into the top level directory
2. Install the dependencies and dev dependencies with:
   ```
   pipenv install -d
   ```
3. Configure environment variables in `.env` file with your API credentials

## Usage

### Running the Application

This project is CLI-only. Run all integrations and write CSVs + logs:

```bash
make cli
```


## Integrations

### Xero

The Xero integration uses OAuth2 authentication to access the accounting API. It allows:
- Fetching bank transactions
- Processing transaction data
- Displaying transaction summaries for different accounts

### GoCardless

The GoCardless integration retrieves:
- Direct debit payments
- Payouts
- Refunds

It converts these into standardized transaction objects for further processing.

### SumUp

The SumUp integration fetches:
- Card payments
- Payouts
- Transaction fees

It converts these into standardized transaction objects for further processing.

### OSM

The OSM integration fetches:
- Spend card transactions
- Top up transactions

It converts these into standardized transaction objects for further processing.

## Development

### Version Control

We use [Semantic Commits](https://gist.github.com/joshbuchea/6f47e86d2510bce28f8e7f42ae84c716) for commit messages and follow [trunk based development](https://trunkbaseddevelopment.com).

Example workflow:

```bash
git checkout main
git pull
git checkout -b feat/some-feature
git add .
git commit -m "feat: feature description"
git push -u origin feat/some-feature
```

### Release

[Semantic release](https://python-semantic-release.readthedocs.io/en/latest/) is used to manage the release process. Releases are automated and triggered by merges to the main branch.

## License

MIT License. See 'LICENSE' for more information.
