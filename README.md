# DIVE_Doc_plateform

## Description


### Installation & Setup
1- Install dependencies
```bash
conda create divedoc-plateform-env
conda activate divedoc-plateform-env
pip install -r requirements.txt
```

2- Install the git hook
I add a git hook that is executed before each push locally and run : <br>
 - bandit: to check security issues
 - ruff: to check quality and format
 - pytest: to check main functions' sanity
```bash
pre-commit install --hook-type pre-push
```

3- Run the sever locally
```bash
#terminal 1
python app.py
```

```bash
#terminal 2
uvicorn src.main:app --host 127.0.0.1 --port 8000
```
