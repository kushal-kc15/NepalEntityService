# Nepal Entity Service - Jupyter Notebooks

This directory contains interactive Jupyter notebooks demonstrating data maintenance workflows with the Nepal Entity Service (nes2). All notebooks use authentic Nepali political data.

## Prerequisites

1. Install Jupyter:
   ```bash
   poetry add --group dev jupyter
   ```

2. Install the nes2 package:
   ```bash
   poetry install
   ```

3. Start Jupyter:
   ```bash
   poetry run jupyter notebook
   ```

## Notebooks

### 1. Entity Management (`01_entity_management.ipynb`)

Learn the fundamentals of entity management with interactive examples.

**Topics:**
- Initialize services
- Create entities with multilingual names
- Retrieve and search entities
- Update entities with automatic versioning
- View version history
- Batch entity creation

**Best for:** Getting started with the Publication Service

---

### 2. Relationship Management (`02_relationship_management.ipynb`)

Explore how to create and manage relationships between entities.

**Topics:**
- Create party membership relationships
- Add temporal information (start/end dates)
- Query relationships by entity
- Query relationships by type
- Update relationships
- View relationship version history
- Explore relationship networks

**Best for:** Understanding entity connections and political affiliations

---

### 3. Data Import Workflow (`03_data_import_workflow.ipynb`)

Complete workflow for importing data from external sources.

**Topics:**
- Prepare import data
- Validate data before import
- Check for duplicates
- Batch import entities
- Handle import errors
- Verify imported data
- Generate import reports

**Best for:** Bulk data operations and migrations

---

### 4. Data Quality Analysis (`04_data_quality_analysis.ipynb`)

Analyze and improve data quality with comprehensive checks.

**Topics:**
- Database statistics
- Identify missing data
- Check naming consistency
- Validate relationship integrity
- Analyze version history
- Generate quality reports with scores

**Best for:** Maintaining high data quality standards

---

## Running the Notebooks

### Option 1: Jupyter Notebook (Classic)

```bash
poetry run jupyter notebook
```

Then navigate to the `notebooks/` directory and open any notebook.

### Option 2: JupyterLab (Modern Interface)

```bash
poetry add --group dev jupyterlab
poetry run jupyter lab
```

### Option 3: VS Code

1. Install the Jupyter extension in VS Code
2. Open any `.ipynb` file
3. Select the Python interpreter from your poetry environment

## Notebook Structure

Each notebook follows this structure:

1. **Introduction** - Overview and learning objectives
2. **Setup** - Import modules and initialize services
3. **Main Content** - Interactive examples with explanations
4. **Summary** - Key takeaways and next steps

## Tips for Using the Notebooks

### Running Cells

- **Shift + Enter**: Run current cell and move to next
- **Ctrl + Enter**: Run current cell and stay
- **Alt + Enter**: Run current cell and insert new cell below

### Async/Await

All notebooks use async/await syntax. Jupyter automatically handles this with the `await` keyword at the top level.

### Modifying Examples

Feel free to modify the examples! Try:
- Changing entity data
- Adding your own entities
- Experimenting with different queries
- Creating custom relationships

### Saving Your Work

Notebooks automatically save, but you can also:
- **Ctrl + S**: Manual save
- **File → Download as**: Export in various formats

## Common Patterns

### Initialize Services

```python
from pathlib import Path
from nes2.database.file_database import FileDatabase
from nes2.services.publication import PublicationService

db_path = Path("../nes-db/v2")
db = FileDatabase(base_path=str(db_path))
pub_service = PublicationService(database=db)
```

### Create an Entity

```python
entity_data = {
    "slug": "example-entity",
    "type": "person",
    "sub_type": "politician",
    "names": [
        {
            "kind": "PRIMARY",
            "en": {"full": "Example Name"},
            "ne": {"full": "उदाहरण नाम"}
        }
    ]
}

entity = await pub_service.create_entity(
    entity_data=entity_data,
    author_id="author:human:notebook-user",
    change_description="Created via notebook"
)
```

### Search Entities

```python
from nes2.services.search import SearchService

search_service = SearchService(database=db)
results = await search_service.search_entities(
    query="search term",
    entity_type="person",
    limit=10
)
```

## Troubleshooting

### "Database not found" Error

Make sure the database path is correct. The notebooks assume the database is at `../nes-db/v2` relative to the notebooks directory.

### "Module not found" Error

Ensure you're running Jupyter from the poetry environment:
```bash
poetry run jupyter notebook
```

### Async Errors

If you see errors about async/await, make sure you're using `await` for all async functions:
```python
# Correct
entity = await pub_service.get_entity(entity_id)

# Incorrect
entity = pub_service.get_entity(entity_id)  # Missing await
```

## Data Files

The notebooks work with the database at `nes-db/v2`. If you don't have data yet:

1. Run the example scripts in `examples/` to create sample data
2. Import data using `03_data_import_workflow.ipynb`
3. Use the API to populate data

## Next Steps

After completing the notebooks:

1. Review the example scripts in `examples/`
2. Read the Data Maintainer Guide in `docs/data-maintainer-guide.md`
3. Build your own data maintenance workflows
4. Explore the API documentation at `/docs`

## Contributing

If you create useful notebooks:

1. Follow the existing structure
2. Use authentic Nepali data
3. Include clear explanations
4. Add to this README

## Support

For questions or issues:
- Check the documentation in `docs/`
- Review the example scripts in `examples/`
- Refer to the API documentation
