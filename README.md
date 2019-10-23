## ncep https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/cdus/degree_days/

### A paritial list of system requirements
- Python version 3.7.x
- [PROJ](https://proj.org/install.html)
  - On Debian/Ubuntu:
    - `sudo apt-get install proj-bin`
    - `sudo apt-get install libproj-dev`
- [GEOS](https://trac.osgeo.org/geos/)
  - On Debian/Ubuntu:
    - `sudo apt-get install libgeos-dev`

### Project installation
- clone this repository
- `python setup.py install`
- `pip install -r requirements.txt`

### Basic use
- `cd ncep/ncep/`
- `python ncep_main.py`

![image](https://user-images.githubusercontent.com/49287206/67347675-cd0d6600-f510-11e9-8e8c-d1cd902a21d3.png)
