# Pyvidia Update Checker

The Pyvidia Update checker is a simple python program for those, who installed the Nvidia Drivers on their
Windows System without the GeForce Experience app. Instead of checking the Nvidia Driver Download page
manually, the Pyvidia update checker can read your systems driver version and checks the current driver version
from the official Nvidia page.

## Disclaimer

This software is an independent creation and is not affiliated with NVIDIA or any other entity.

# Participation

This is a simple Python project I've written in my free time and anyone is welcome to participating
in further improvements and development. If you want to improve something or add new features, please
open a new issue with the appropriate label. Due to its low complexity, this project is ideal for
beginners and there is plenty of room for improvements, since I started this project to be functional
as fast as possible without thinking too much about a good architecture. Furthermore, this is my first time
using Python to create a GUI app with [wxPython](https://wxpython.org/), so do not take this approach as
good practise.

## Local setup
### Requirements

- Python 3.12
- [Poetry](https://python-poetry.org/)

### Setup

Use poetry to initialize a virtual environment and install the required packages, including the one from the
dev group:

```bash
poetry env use $(which python3.12)
poetry install --with dev
```

If you want to improve the Download page scraper, you also need to install the scraper requirements:

```bash
poetry install --with dev --with scraper
```

Initialize the pre-commit hooks:

```bash
pre-commit install
```

From here on you are ready to go. To start the GUI, run:

```bash
poetry run python -m pyvidia_update.ui.app
```

To start the scraper cli program, run:

```bash
poetry run python -m scraper.nvidia_driver_dropdowns
```
