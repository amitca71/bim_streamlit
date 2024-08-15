# Requirements
- [Poetry](https://python-poetry.org) for dependency managament.
- Duplicate the `secrets.toml.example` file to `secrets.toml` and populate with appropriate keys.

## Usage
```
poetry update
poetry run streamlit run bim_streamlit/main.py --server.port=80
