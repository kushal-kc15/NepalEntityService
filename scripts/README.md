# Development Scripts

## Format Script

Run the format script before committing to automatically fix formatting:

```bash
./scripts/format.sh
```

This script will:
- Apply black formatting (line length: 88)
- Sort imports with isort (compatible with black)
- Check for linting issues with flake8

If flake8 reports any issues, fix them manually before committing.

## Check Format (CI Mode)

Run the script with `--check` flag to verify formatting without modifying files (used in CI):

```bash
./scripts/format.sh --check
```

This will:
- Check black formatting (no changes)
- Check import sorting (no changes)
- Check for linting issues with flake8

This is the same check that runs in CI, so running it locally ensures your code will pass.

## Tool Configuration

All formatting tools are configured to work together:

- **Black**: Auto-formats code with 88 character line length
- **isort**: Sorts imports using black-compatible profile
- **flake8**: Lints code with black-compatible rules

Configuration files:
- `pyproject.toml`: black and isort settings
- `.flake8`: flake8 settings

## Manual Checks

You can also run individual tools:

```bash
# Format code
poetry run black .
poetry run isort .

# Check formatting (without modifying files)
poetry run black --check .
poetry run isort --check-only .

# Lint code
poetry run flake8 .
```
