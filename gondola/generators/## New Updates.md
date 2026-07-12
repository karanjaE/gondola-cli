The `gondola init ...` or `gondola i` command to create a new projject should now be interactive where:

- User types the command `gondola init` or `gondola i`
- It prompts the user for:
  - Project name (which should be in lowercase/snake_case format)
  - Database engine(gives the user the option to select between: postgres, mysql, mariadb, sqlite)
  - Whether to include docker files(gives the user the option to select between: Yes, No)
  - Whether to include extensions(gives the user the option to select between: Yes, No)
  - What extensions to include(gives the user the option to select from a list of extensions: postgis, pgvector, etc)
- Default values should be:
  - Project name: `my-fastapi-project`
  - Database engine: `postgres`
  - Include docker files: `Yes`
  - Include extensions: `No`
  - Extensions: `[]`
  
  Update this and also update the readme.md to reflect the changes.
