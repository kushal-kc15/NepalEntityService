# Development Scripts

## Format Script

Run the format script before committing to ensure your code passes CI checks:

```bash
./scripts/format.sh
```

This script will:
- Apply black formatting
- Sort imports with isort
- Check for linting issues with flake8

If flake8 reports any issues, fix them manually before committing.
