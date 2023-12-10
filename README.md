# COMPIPE  (WIP)

Compipe is a lightweight command manager specifically designed to automate tasks.


### Example of initializing runtime environment and credential keys

```python

credentials_cfg_path = os.path.join(os.path.dirname(__file__), 'credential/keys.json')

runtime_cfg_path = os.path.join(os.path.dirname(__file__), 'tars_server_runtime_env.json')

# config DEBUG environment
initialize_runtime_environment(params={ARG_DEBUG: False},
                               runtime_cfg_path=runtime_cfg_path,
                               credential_cfg_path=credentials_cfg_path)


```

### How to run unittest

- Add "entry_points" to setup.py
  ```text
    setup(
        # ... other setup parameters ...
        entry_points={
            'console_scripts': [
                'unittest = compipe.unittest.cmd_test:main',
            ],
        }
    )

  ```
- Install Your Package in Editable Mode:
  ```text
  pip install -e .
  ```

- Add PYPI API token to system environment
  ```text
  set PYPI_API_TOKEN=<Your-API-Token>
  ```
- Run `upload.bat` to upload package wheel