@echo off

:: Create a virtual environment
python -m venv venv

:: Activate the virtual environment
call venv\Scripts\activate

:: Upgrade pip to the latest version
python -m pip install --upgrade pip

:: Install dependencies from requirements.txt
pip install -r requirements.txt

:: Deactivate the virtual environment
deactivate

echo Virtual environment setup and dependencies installed successfully.
