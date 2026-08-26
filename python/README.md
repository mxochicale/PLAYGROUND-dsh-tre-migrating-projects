# End-to-End Migration Pipeline for a Python Project

This guide walks through moving a Python project from the DSH (Data Safe Haven) into the ARC TRE (Trusted Research Environment), packaging it as a Docker container along the way.

## Overview

```mermaid
flowchart LR
    A["<b>DSH</b><br/>1. Prepare & test"] --> B["<b>DSH</b><br/>2. Package code and dependencies"]
    B --> C["<b>Local machine</b><br/>3. Build Docker container"]
    C --> D["<b>ARC TRE</b><br/>4. Bring in container image and data"]
    D --> E["<b>ARC TRE</b><br/>5. Check the code works"]
```

Five steps, three environments:

1. **DSH** prepare and test your code.
2. **DSH** package the code and its dependencies.
3. **Local machine** build the code into a Docker container.
4. **ARC TRE** bring the container image and data in through the Airlock.
5. **ARC TRE** confirm the code runs correctly.

---

## Step 1. DSH: Prepare and Test Your Code

Log in to your DSH (Data Safe Haven) and prepare the files to be compressed into an archive.

**Dependency tracking**

To ensure reproducibility, it is recommended that your project includes a pyproject.toml file to track package versions. 
Alternatively, you can create a requirements.txt file listing all dependencies alongside their versions.

Whichever approach you choose, you can cross-check it against the packages installed in your Jupyter Lab session using:

```bash
pip list
```

**Organising your project**

For easier migration and scalability across environments, it is good practice to consolidate your files into a single repository before extraction.

It is worth testing this process both in the DSH and on your local machine, to confirm that you are packaging and compressing all relevant files, including Python package dependencies, scripts, and, where applicable, unit tests.

Generally speaking, this allows you to:

* Clone the project cleanly into any environment
* Record its version and a timestamp for traceability
* Ensure the packaged copy can always be traced back to an exact commit


For example:
```bash
git clone https://github.com/mxochicale/PLAYGROUND-dsh-tre-migrating-projects.git
cd PLAYGROUND-dsh-tre-migrating-projects
VERSION=$(git rev-parse --short HEAD)
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
```

At this point, develop and test your code as normal within the DSH.


## Step 2. DSH: Package the code and dependencies

Compress the project folder into a versioned, timestamped zip file:

```bash
cd ..
zip -r "githubproject-${VERSION}-${TIMESTAMP}.zip" PLAYGROUND-dsh-tre-migrating-projects
```

> **Note:** zip the same folder you cloned into (here, `PLAYGROUND-dsh-tre-migrating-projects`). Double-check the folder name matches your project before running this.

To unzip it again elsewhere:

```bash
unzip githubproject-*.zip
```

---

## Step 3. Local machine: python virtual environment and build the Docker container

### Working with a virtual environment (uv)

Install `uv` (macOS and Linux):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Create a virtual environment and install the project's dependencies:

```bash
uv venv --python 3.12.1
uv pip install -e ".[test]"
```

Activate environment and run unit tests
```bash
source .venv/bin/activate
pytest tests/test_pyproject_versions.py -v
```
Activate the environment and launch Jupyter Lab:

```bash
source .venv/bin/activate
jupyter lab
```

When you're done:

- Log out from the Jupyter menu, or press `Ctrl-C` in the terminal to stop it.
- If a Jupyter process is left running, kill it with:
  ```bash
  pkill -f jupyter
  ```

Remove the virtual environment once you no longer need it:

```bash
rm -rf .venv
```

### Converting notebooks to scripts

If your work is in a notebook, convert it to a plain Python script before packaging:

```bash
jupyter nbconvert --to script <notebook-filename.ipynb>
```

### Build the image with metadata baked in

Tagging the image with the version, git commit, and build date makes it easy to trace later.

```bash
VERSION=0.0.2
GIT_SHA=$(git rev-parse --short HEAD)
BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

docker build \
  --label "org.opencontainers.image.version=${VERSION}" \
  --label "org.opencontainers.image.revision=${GIT_SHA}" \
  --label "org.opencontainers.image.created=${BUILD_DATE}" \
  --no-cache \
  -t my_container:${VERSION} .
```

Shows built image
```bash
$docker images
IMAGE                     ID             DISK USAGE   CONTENT SIZE   EXTRA
my_container:0.0.1        4bc2c9cfe93b       2.08GB          507MB
my_container:0.0.2        15c34e2b552a       2.51GB          589MB
```

### Test the image locally

Run docker file with the defatul unit test
```
docker run -it --rm my_container:$VERSION
```

Using bash
```bash
docker run -it --rm my_container:$VERSION bash
# then, inside the container:
# python dsh-tre-code/00-dsh-jupyter-lab-session.py
# pytest tests/test_pyproject_versions.py -v
```

### Save and checksum the image

Save the image to a tarball and generate a checksum, so you (and the TRE reviewers) can confirm it hasn't been altered in transit.

```bash
OUTDIR=~/Downloads
IMAGENAME=my_container_$VERSION.tar.gz

docker save my_container:$VERSION | gzip > "${OUTDIR}/${IMAGENAME}"
cd "${OUTDIR}" && sha256sum "${IMAGENAME}" > "${IMAGENAME}.sha256"
```

---

## Step 4. ARC TRE: Bring in the container image and data

Upload `my_container_$VERSION.tar.gz` and its checksum file to the TRE through the [Airlock](https://tre.arc.ucl.ac.uk/). 

Then, from the terminal in the TRE desktop:

```bash
VERSION=0.0.2
INDIR=~/shared/inbound/$(whoami)
cd "${INDIR}"

sha256sum -c my_container_$VERSION.tar.gz.sha256
docker load -i my_container_$VERSION.tar.gz
```

`sha256sum -c` confirms the file matches the checksum generated in Step 3, before you load it.

---

## Step 5. ARC TRE: Check the code works

Run the container inside the TRE exactly as you did locally, to confirm it behaves the same way:

```bash
docker run -it docker.io/library/my_container:$VERSION
```

Run bash
```bash
docker run -it docker.io/library/my_container:$VERSION bash
# then, inside the container:
# python dsh-tre-code/00-dsh-jupyter-lab-session.py
# pytest tests/test_pyproject_versions.py -v
```

If this runs without errors and produces the expected output, the migration is complete.
