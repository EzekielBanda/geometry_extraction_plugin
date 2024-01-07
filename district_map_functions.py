import os
from qgis.utils import iface
from qgis.core import (
    QgsVectorLayer,
    QgsVectorFileWriter,
    QgsFields, QgsFeature,
    QgsGeometry, QgsExpression, QgsProject,
    QgsFeatureRequest, Qgis, QgsMessageLog
)


def extract_district_map(district_name, input_layer):
    # Check if the provided layer is valid
    if not input_layer or not input_layer.isValid():
        print("Invalid layer!")
        return

    # Get the current visible extent of the map canvas
    canvas_extent = iface.mapCanvas().extent()
    # Get the directory of the original shapefile
    input_source = input_layer.source()
    input_directory = os.path.dirname(input_source)

    # Define the output shapefile path in the same directory
    output_shapefile = os.path.join(input_directory, district_name + '_district.shp')

    # Get the CRS of the input layer
    input_crs = input_layer.crs()

    # Create a new memory layer with the CRS of the input layer
    memory_layer = QgsVectorLayer("Polygon?crs={}".format(input_crs.authid()), "output_district", "memory")
    memory_layer.startEditing()

    # Define the fields for the new layer based on the fields of the original layer
    fields = QgsFields()
    for field in input_layer.fields():
        fields.append(field)

    # Add the fields to the new layer
    memory_layer.dataProvider().addAttributes(fields)
    memory_layer.updateFields()

    # Create a query to select features based on the district name
    expr = QgsExpression('"DISTRICT" = \'{0}\''.format(district_name))
    request = QgsFeatureRequest(expr)

    # Loop through the features of the original layer based on the query
    for original_feature in input_layer.getFeatures(request):
        # Create the feature for the new layer
        feature = QgsFeature(fields)

        # Check if the extent of the extracted feature is within the visible extent
        if not canvas_extent.contains(feature.geometry().boundingBox()):
            # Adjust the map canvas extent to include the extracted feature
            canvas_extent.combineExtentWith(feature.geometry().boundingBox())

        # Set the geometry of the new feature
        feature.setGeometry(QgsGeometry.fromWkt(original_feature.geometry().asWkt()))

        # Set the district name in the 'DISTRICT' field
        feature['DISTRICT'] = district_name

        # Copy attribute values from the original feature to the new feature
        for field in fields:
            field_name = field.name()
            if field_name != 'DISTRICT':  # Skip the 'DISTRICT' field
                feature[field_name] = original_feature[field_name]

        # Add the feature to the new layer
        memory_layer.addFeature(feature)

    # Commit the changes to the memory layer
    memory_layer.commitChanges()

    # Save the memory layer to a new shapefile in the same directory as the original
    QgsVectorFileWriter.writeAsVectorFormat(
        memory_layer, output_shapefile, 'utf-8', input_crs, 'ESRI Shapefile')

    # Add the new layer to the project with a modified name
    layer_name = district_name + '_district'
    QgsProject.instance().addMapLayer(memory_layer)
    memory_layer.setName(layer_name)
    memory_layer.triggerRepaint()

    # Set the map canvas extent to include the extracted features# ...
    QgsMessageLog.logMessage("Layer added to the map canvas: {}"
                             .format(memory_layer.name()),
                             'district_map_extractor',
                             Qgis.Info)

    iface.mapCanvas().setExtent(canvas_extent)
    iface.mapCanvas().refresh()
