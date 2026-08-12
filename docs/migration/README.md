# dhs-tre migration

## Compress and uncompress project
```bash
git clone https://github.com/mxochicale/test-dhs-tre-migrated-git-projects.git
cd test-dhs-tre-migrated-git-projects
VERSION=$(git rev-parse --short HEAD)
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
cd ..
zip -r "githubproject-${VERSION}-${TIMESTAMP}.zip" test-dhs-tre-migrated-git-projects
```

```bash
unzip *.zip
```
