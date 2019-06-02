<img src="https://github.com/radiantearth/stac-site/raw/master/images/logo/stac-030-long.png" alt="stac-logo" width="700"/>

## About

The SpatioTemporal Asset Catalog (STAC) specification aims to standardize the way geospatial assets are exposed online and queried. 
A 'spatiotemporal asset' is any file that represents information about the earth captured in a certain space and 
time. The initial focus is primarily remotely-sensed imagery (from satellites, but also planes, drones, balloons, etc), but 
the core is designed to be extensible to SAR, full motion video, point clouds, hyperspectral, LiDAR and derived data like
NDVI, Digital Elevation Models, mosaics, etc. 

The goal is for all major providers of imagery and other earth observation data to expose their data as SpatioTemporal Asset 
Catalogs, so that new code doesn't need to be written whenever a new JSON-based REST API comes out that makes its data 
available in a slightly different way. This will enable standard library components in many languages. STAC can also be
implemented in a completely 'static' manner, enabling data publishers to expose their data by simply publishing linked JSON
files online.

## Building

To build the plugin and deploy to your plugin directory you will need the [pb_tool](http://g-sherman.github.io/plugin_build_tool/) CLI tool.

To compile the plugin run `pb_tool compile` in the root directory of this repository. 
Compiling is needed any time the resources.py file needs to be rebuilt. 
To deploy the application to your QGIS plugins directory run `pb_tool` deploy and reload the plugin within QGIS.
It's recommended to use the Plugin Reloader plugin within QGIS to easily reload the plugin during development.
## Current version and branches

The [master branch](https://github.com/kbgg/qgis-stac-browser/tree/master) is the 'stable' version of the spec. It is currently version 
**0.1** of the plugin. The 
[dev](https://github.com/kbgg/qgis-stac-browser/tree/dev) branch is where active development takes place. 
Whenever dev stabilizes a release is cut and we merge dev in to master. So master should be stable at any given time.
It is possible that there may be small releases in quick succession, especially if they are nice improvements that do 
not require lots of updating.

## In this Repository

This repository contains the core specifications plus examples and validation schemas and tools. Also included are a
few documents that provide more context and plans for the evolution of the specification. Each spec folder contains a
README explaining the layout of the folder, the main specification document, examples, validating schemas and OpenAPI
documents (if relevant). The four specifications detailed are meant to be used together, but are designed so each piece
is small, self-contained and reusable in other contexts.

**[item-spec/](item-spec/)** defines a STAC Item, which is a [GeoJSON](http://geojson.org) Feature
with additional fields for things like time, links to related entities and assets (including thumbnails). This is the 
atomic unit that describes the data to be discovered.

**[catalog-spec/](catalog-spec/)** specifies a structure to link various STAC Items together to be crawled or browsed. It is a
simple, flexible JSON file of links to Items, Catalogs or Collections that can be used in a variety of ways.

**[collection-spec/](collection-spec/)** provides additional information about a spatio-temporal collection of data.
In the context of STAC it is most likely a collection of STAC Items that is made available by a data provider.
It includes things like the spatial and temporal extent of the data, the license, keywords, etc.
It enables discovery at a higher level than individual items, providing a simple way to describe sets of data.

**[api-spec/](api-spec/)** extends the core publishing capabilities of STAC with an active REST search endpoint that returns
just the Items a user requests in their query. It is specified as a couple [OpenAPI](http://openapis.org) documents, one
[standalone](api-spec/STAC-standalone.yaml) and one that is [integrated with WFS3](api-spec/WFS3core%2BSTAC.yaml) 
(see [WFS3 on GitHub](https://github.com/opengeospatial/wfs_fes) for info on it). The documents also include the `/stac/` 
endpoint which is a way for a dynamic server to provide catalog and collection browsing.

**Extensions:** The *[extensions/](extensions/)* folder is where extensions live. Extensions can extend the 
functionality of the core spec or add fields for specific domains.

**Additional documents** include the current [roadmap](roadmap.md) and a complementary [how to help](how-to-help.md)
document, a [list of implementations](implementations.md), 
and a discussion of the collaboration [principles](principles.md) and specification approach.

