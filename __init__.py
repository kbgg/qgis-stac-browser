# -*- coding: utf-8 -*-
"""
/***************************************************************************
 STACBrowser
                                 A QGIS plugin
 This plugin searches for and downloads assets from STAC catalogs
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2019-05-28
        copyright            : (C) 2019 by Kevin Booth
        email                : kevin@kb.gg
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load STACBrowser class from file STACBrowser.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .stac_browser import STACBrowser
    return STACBrowser(iface)
