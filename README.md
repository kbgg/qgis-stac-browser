<img src="https://github.com/radiantearth/stac-site/raw/master/images/logo/stac-030-long.png" alt="stac-logo" width="700"/>

## About

The QGIS STAC Browser plugin allows for searching STAC catalogs for assets and downloading those assets directly into QGIS.

## Current version and branches

The [master branch](https://github.com/kbgg/qgis-stac-browser/tree/master) is the 'stable' version of the plugin. It is currently version 
**0.1** of the plugin. The 
[dev](https://github.com/kbgg/qgis-stac-browser/tree/dev) branch is where active development takes place. 
Whenever dev stabilizes a release is cut and we merge dev in to master. So master should be stable at any given time.
It is possible that there may be small releases in quick succession, especially if they are nice improvements that do 
not require lots of updating.

## Contributing

Please read the [contributing guide](CONTRIBUTING.md) before submitting any pull requests.

## Building

To build the plugin and deploy to your plugin directory you will need the [pb_tool](http://g-sherman.github.io/plugin_build_tool/) CLI tool.

To compile the plugin run the following command in the root directory of this repository:
 
    pb_tool compile
     
Compiling is needed any time the resources.py file needs to be rebuilt. 

To deploy the application to your QGIS plugins directory run the following command and reload the plugin within QGIS:

    pb_tool deploy 

It's recommended to use the Plugin Reloader plugin within QGIS to easily reload the plugin during development.

### Troubleshooting

#### pyuic5 is not in your path

    pyuic5 is not in your path---unable to compile your ui files
    pyrcc5 is not in your path---unable to compile your resource file(s)

Fix: 

    export PATH=/anaconda3/bin:$PATH

#### QGIS cannot find plugin 

Change pb_tool.cfg settings:

Mac

    plugin_path: /Users/{USER}/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/

Linux

    plugin_path: /home/{USER}/.local/share/QGIS/QGIS3/profiles/default/python/plugins

Windows

    plugin_path: C:\Users\{USER}\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins
