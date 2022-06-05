## dbdump

This script helps to backup MySQL and MariaDB databases.

### Requirements
- linux / freebsd / openbsd/ netbsd/ macOS
- mysqldump
- python3
- pyyaml

### Preparing the environment
Although not mandatory, it is recommended that the script work with python's virtualenv. This will make you isolate your dependencies and make sure everything works properly.

#### Creating venv
```bash
python -m venv .venv
```

#### Using venv
```bash
source .venv/bin/activate
```

### Installing dependencies
#### pyyaml
```bash
pip install pyyaml
```

### Examples of config.yaml
```yaml
databases:
  - db_demo_01_prd:
      db_host: "127.0.0.1"
      db_name: "db_demo_01_prd"
      db_username: "db_username_here"
      db_password: "db_password_here"
      dump_dir: "./dumps"
      excluded_tables:
        - exclude_table_01
        - exclude_table_02
  - db_demo_02_prd:
      db_host: "127.0.0.1"
      db_name: "db_demo_02_prd"
      db_username: "db_username_here"
      db_password: "db_password_here"
      dump_dir: "./dumps"
```
