# dhs-tre migration

## Compress and uncompress project
```bash
git clone https://github.com/mxochicale/PLAYGROUND-dsh-tre-migrating-projects.git
cd PLAYGROUND-dsh-tre-migrating-projects.git
VERSION=$(git rev-parse --short HEAD)
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
cd ..
zip -r "githubproject-${VERSION}-${TIMESTAMP}.zip" test-dhs-tre-migrated-git-projects
```

```bash
unzip *.zip
```
