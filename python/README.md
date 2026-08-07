# intro-to-deep-learning from carpentries-lab

## Main references
* https://carpentries-lab.github.io/deep-learning-intro/
* https://jose.theoj.org/papers/10.21105/jose.00307
* https://github.com/carpentries-lab/deep-learning-intro/tree/main

## Local development
1. Install uv (macOS and Linux)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

# Create a virtual environment and install dependencies
```bash
uv venv
uv pip install -e .
```

## Launch env and jupyter notebooks

```bash
source .venv/bin/activate #activate VE
jupyter lab
# logout from the menu
# ctrl-c to exit
# kill them
# pkill -f -1 jupyter*
```

## Remove envorinment
```bash
rm -rf .venv
```


## Convert jupyter notebooks to python scripts
```bash
jupyter nbconvert --to script <notebook-filename.ipynb> 
```


## Clone repo
```bash
git clone https://github.com/mxochicale/intro-to-deep-learning-carpentries-lab.git
```

