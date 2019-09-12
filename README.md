## ncep https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/cdus/degree_days/

### A paritial list of system requirements
- Python version 3.7.x
- [PROJ](https://proj.org/install.html)
  - On Debian:
    - `sudo apt-get install proj-bin`
    - `sudo apt-get install libproj-dev`
- [GEOS](https://trac.osgeo.org/geos/)
  - On Debian:
    - `sudo apt-get install libgeos-dev`

### Project installation
- clone this repository
- `python setup.py install`
- `pip install -r requirements.txt`

### Basic use
- `cd ncep/ncep/`
- `python ncep_main.py`

