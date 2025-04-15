# Unzip processor

Simple processor unzipping files in the `data/in/files` and storing results in `data/out/files`.

### Supported file formats:
- .7z
- .tar.bz2
- .tbz2
- .gz
- .tar.gz
- .tgz
- .tar
- .tar.xz
- .txz
- .zip

**NOTE** The reason for writing this is that the keboola-decompress processor can't handle situations when files in the zipfile 
contain (back)slash characters, e.g. `\filename.xml`

**Table of contents:**  
  
[TOC]



# Configuration

### Sample configuration

```json
{
    "definition": {
        "component": "kds-team.processor-unzip"
    },
    "parameters": {
        "extract_to_folder" : true,
        "#password_7z" : "password"
    }
}
```
- **extract_to_folder** - boolean to indicate if zipped folders should be extracted to folders within `data/out/files`
  or if files within the zipped folder should be added directly to the `data/out/files`
- **#password_7z** [OPTIONAL] - password for 7zip files.
## Development

If required, change local data folder (the `CUSTOM_FOLDER` placeholder) path to your custom path in the docker-compose file:

```yaml
    volumes:
      - ./:/code
      - ./CUSTOM_FOLDER:/data
```

Clone this repository, init the workspace and run the component with following command:

```
git clone repo_path my-new-component
cd my-new-component
docker-compose build
docker-compose run --rm dev
```

Run the test suite and lint check using this command:

```
docker-compose run --rm test
```

# Integration

For information about deployment and integration with KBC, please refer to the [deployment section of developers documentation](https://developers.keboola.com/extend/component/deployment/) 