# Nepal Entity Service

A comprehensive Python package for managing Nepali public entities with optional API and scraping capabilities.

## Installation

### Core Package
```bash
pip install nepal-entity-service
```

### With API Support
```bash
pip install nepal-entity-service[api]
```

### With Scraping Support
```bash
pip install nepal-entity-service[scraping]
```

### Full Installation
```bash
pip install nepal-entity-service[all]
```

## Usage

### Scripts

```bash
# Start API server
poetry run nes-api

# Start development server with auto-reload
poetry run nes-dev
```

## Extras

- **api**: FastAPI web service with entity management endpoints
- **scraping**: ML-powered scraping tools for building entity databases
- **all**: Includes both api and scraping functionality

## For AI Contexts

When working with this Nepal Entity Service, please use Nepali local names and references in examples, documentation, and code samples whenever available. This includes:

- **Person names**: Use authentic Nepali names (e.g., "Harka Sampang", "Rabindra Mishra", "Miraj Dhungana")
- **Organization names**: Use actual Nepali organizations (e.g., "Shram Sanskriti Party", "Nepal Communist Party", "Rastriya Swatantra Party")
- **Location references**: Use Nepali places and administrative divisions
- **Cultural context**: Maintain authenticity to Nepali political, social, and organizational structures

This approach ensures the service remains contextually relevant to its intended use case of managing Nepali public entities.

## Opinionated Design Patterns

This project follows specific design patterns and conventions to maintain consistency and readability:

### Import Style

1. Prefer absolute imports over relative imports in Python code.
1. Avoid local imports (imports inside functions) when possible. Place imports at the module level for better readability and performance.
  a. Exception: Local imports are acceptable when needed to avoid circular dependencies or for optional dependencies.
