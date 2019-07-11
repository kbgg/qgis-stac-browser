from typing import Any, Union

from qgis.core import (QgsCoordinateReferenceSystem, QgsProject,
                       QgsCoordinateTransform)

EasyCrs = Union[int, QgsCoordinateReferenceSystem]

"""Commnly used EPSG:4326 CRS."""
crs4326 = QgsCoordinateReferenceSystem(4326)


def get_project_crs():
    """Return the project CRS."""
    return QgsProject.instance().crs()


def transform(from_crs: EasyCrs, to_crs: EasyCrs, geom: Any) -> Any:
    """Try to transform whatever is passed as geometry."""
    if isinstance(from_crs, int):
        from_crs = crs4326 if from_crs == 4326 else QgsCoordinateReferenceSystem(from_crs)

    if isinstance(to_crs, int):
        to_crs = crs4326 if to_crs == 4326 else QgsCoordinateReferenceSystem(to_crs)

    transform = QgsCoordinateTransform(from_crs, to_crs, QgsProject.instance())

    assert transform.isValid()

    return transform.transform(geom)
