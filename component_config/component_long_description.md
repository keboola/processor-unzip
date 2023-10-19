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
        "extract_to_folder" : true
    }
}
```
- **extract_to_folder** - boolean to indicate if zipped folders should be extracted to folders within `data/out/files`
  or if files within the zipped folder should be added directly to the `data/out/files`