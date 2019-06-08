<img src="https://github.com/radiantearth/stac-site/raw/master/images/logo/stac-030-long.png" alt="stac-logo" width="700"/>

## About

The QGIS STAC Browser plugin allows for searching STAC catalogs for assets and downloading those assets directly into QGIS.
## Building

To build the plugin and deploy to your plugin directory you will need the [pb_tool](http://g-sherman.github.io/plugin_build_tool/) CLI tool.

To compile the plugin run `pb_tool compile` in the root directory of this repository. 
Compiling is needed any time the resources.py file needs to be rebuilt. 
To deploy the application to your QGIS plugins directory run `pb_tool` deploy and reload the plugin within QGIS.
It's recommended to use the Plugin Reloader plugin within QGIS to easily reload the plugin during development.
## Current version and branches

The [master branch](https://github.com/kbgg/qgis-stac-browser/tree/master) is the 'stable' version of the plugin. It is currently version 
**0.1** of the plugin. The 
[dev](https://github.com/kbgg/qgis-stac-browser/tree/dev) branch is where active development takes place. 
Whenever dev stabilizes a release is cut and we merge dev in to master. So master should be stable at any given time.
It is possible that there may be small releases in quick succession, especially if they are nice improvements that do 
not require lots of updating.
