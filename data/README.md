# Data

Put the PhysioNet **Auricle 1.0.0** dataset here (or point `AURICLE_ROOT` at it):

```bash
wget -r -N -c -np -nH --cut-dirs=3 -P data/auricle-a-multimodal-wearable-sensing-dataset-for-cardiovascular-and-hemodynamic-assessment-1.0.0 \
  https://physionet.org/files/auricle/1.0.0/
# or: export AURICLE_ROOT=/path/to/auricle-a-multimodal-wearable-sensing-dataset-for-cardiovascular-and-hemodynamic-assessment-1.0.0
```

The folder must contain `RECORDS`, `demographics.csv`, `sensor_coordinates.csv` and `data/<record>/<record>.{hea,dat}`.
Dataset DOI: https://doi.org/10.13026/swme-vp69 (https://physionet.org/content/auricle/1.0.0/). It is released under the Open Data Commons Attribution License (ODC-By) and is not redistributed here.
