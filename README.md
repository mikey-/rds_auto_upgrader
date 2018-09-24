# rds_postgres_upgrader [![Build Status](https://travis-ci.org/scottx611x/rds_postgres_upgrader.svg?branch=master)](https://travis-ci.org/scottx611x/rds_postgres_upgrader) [![codecov](https://codecov.io/gh/scottx611x/rds_postgres_upgrader/branch/master/graph/badge.svg)](https://codecov.io/gh/scottx611x/rds_postgres_upgrader)

### Pre-Reqs:
- `python 3`
- AWS credentials [configured properly for `boto3`](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html#configuration)
- An RDS Instance in need of upgrading

### Installation:
- `pip install -r requirements.txt`

### Examples:

- **Upgrade many RDS instances to `10.4` by DbInstanceIdentifers**:
    - `python pg_upgrader.py -ids my-cool-db-a my-cool-db-b`

- **Upgrade many RDS instances to `10.4` by DbInstanceTags**:
    - `python pg_upgrader.py -tags {"Name": "test-rds-name", "owner": "test@example.com"}`

### Running Tests:
- `python tests.py`