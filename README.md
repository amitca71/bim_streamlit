# BIM Magic
The system interacts with BIM (Building Information Modeling) data, and provides answer to question.
The BIM data (in IFC format), is loaded to Neo4j DB, with its entities and relashionship.   
The system leans the relashionships from prompt question and answer, and respond in human language.  
see: https://bim-robot.streamlit.app/

![image](https://github.com/user-attachments/assets/af44c4b8-41dc-40e4-b3f4-e3580b1ff243)
# Requirements
- [Poetry](https://python-poetry.org) for dependency managament.
- Duplicate the `secrets.toml.example` file to `secrets.toml` and populate with appropriate keys.
see: https://bim-robot.streamlit.app/

## Usage
poetry update
poetry run streamlit run bim_streamlit/main.py --server.port=80
