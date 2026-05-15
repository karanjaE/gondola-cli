## New Updates

### 1. Update Existing Commands

#### (i) `gondola run server`

- The command `gondola run server` needs to change to `gondola start` and can be aliased as `gondola s`.
- It should also accept the following optional arguments:
  - `--port` or `-p` which defaults to the value of "PORT" in the env variables. If the env variable is not set, it should default to "8000".
  - `--env` or `-e` which sets the app's runtime mode. This can be either "dev/development" or "prod/production". If not set, it should default to "development". If the environment is development, the app runs in development mode which runs `fastapi dev`. If the environment is production, the app runs in production mode which runs `fastapi run`.
  - `--reload` or `-r` which reloads the app when there are changes in the code. Only works if the environment is development.

#### (ii) `gondola create project <name>`

The command should now change to `gondola init <name>` and should be aliased as `gondola i <name>`. 
- It should accept the following optional arguments:
  - `--db` or `-d` which sets the database engine to be used. This can be either "postgres", "mysql", "mariadb" or "sqlite". If not set, it should default to "postgres".
  - `--docker` or `-x` which should be a boolean flag that determines whether to include docker files in the project. If not set, it should default to true.
  - `--extensions` or `-e` which should be a comma separated list of extensions to be included in the project. If not set, it should default to an empty list. 

#### (iii) `gondola generate model <name>`

The command should now change to `gondola generate model <name>` and should be aliased as `gondola gm <name>`. 
- It should accept the following optional arguments:
  - `--fields` or `-f` which should be a comma separated list of fields to be included in the model. The format should be "name:type". If not set, it should default to an empty list.

