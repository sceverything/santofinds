# Contributing

1. Create a virtual environment.
2. Install the package in editable mode.
3. Run the test suite.
4. Run the example compilation check.
5. Do not commit API tokens or generated data.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
python -m pytest
python -m py_compile examples/*.py
```
