# Artifactory Namespaces

A tool to create JFrog Artifactory permission targets based on predefined namespaces.

### CLI parameters

| Parameter | Environment variable | Default value | Description |
| :--- | :--- | :--- | :--- |
| -c --config-file | CONFIG_FILE | | Path to config yaml file |
| -n --namespaces-file | NAMESPACES_FILE | | Path to namespaces yaml file |
| -o --output-dir | OUTPUT_DIR | | Target directory for generated files |
| -q --quiet |  | | Quiet mode |
| -v --verbose |  | | Verbose mode |

### Config yaml file

Most settings of this app can be defined within a config file.  
This file (parameter `-c`) has the following structure:   

```yaml
repos:
  internal:
    - repo-1
    - repo-2
  thirdparty:
    - thirdparty-repo-1
    - thirdparty-repo-2
groups:
  public: publicgroup
  internal: internalgroup
users:
  public: publicuser
  internal: internaluser
outputDir: ./out/
# json | yaml
outputFormat: json 
```

## `namespaces.yaml`

```yaml
namespaces:
  - name: namespace1
    publicPattern: 
    - pattern1/**
    - pattern2/**
    internalPattern: private1/**,private2/**
    restrictedPattern: restricted1/**
    publicThirdpartyPattern: publicthirdparty1/**
    internalThirdpartyPattern: internalthirdparty1/**
    restrictedThirdpartyPattern: restrictedthirdparty1/**
    write: 
    - group1
    - group2
    users: user1,user2
```

`groups`, `users` und `patterns` can be provided as (comma-separated) string
or yaml list (see above).

# Development

## Build

**App binary**

Building a single binary with `pyinstaller`:

```shell
pyinstaller artifactorynamespaces/main.py --onefile
```

**OCI Container image**

Building image with `buildah`: 
```shell
export TAG=$(date +"%Y%m%d-%H%M%S");buildah bud -t docker.io/kwening/artifactorynamespaces:$TAG
buildah push docker.io/kwening/artifactorynamespaces:$TAG
```
