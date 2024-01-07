# -*- coding: utf-8 -*-
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.utils import iface
import os
from .district_map_functions import extract_district_map
from qgis.core import QgsMapLayerType
from .layer_added_listener import LayerAddedListener

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'district_map_extractor_dialog_base.ui'))


class DistrictMapExtractorDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(DistrictMapExtractorDialog, self).__init__(parent)
        self.setupUi(self)
        self.extract_button = self.findChild(QtWidgets.QPushButton, 'extract_button')
        self.layer_listener = LayerAddedListener()
        self.layer_listener.layer_added.connect(self.update_shapefile_path)

        # Disconnect existing connections, if any
        self.extract_button.clicked.disconnect()

        # Access the shapefile_path_label directly
        self.shapefile_path_label = self.findChild(QtWidgets.QLabel, 'shapefile_path_label')
        self.district_combo_box = self.findChild(QtWidgets.QComboBox, 'district_combo_box')

        # Add this line to populate the combo box with district names
        self.populate_district_combo_box()

        self.extract_button.clicked.connect(self.on_extract_button_clicked)

    def populate_district_combo_box(self):
        # Get the active layer
        active_layer = iface.activeLayer()

        # Check if a layer is selected and it is a vector layer
        if active_layer and active_layer.isValid() and active_layer.type() == QgsMapLayerType.VectorLayer:
            # Possible variations of the district field name
            district_field_names = ['District', 'district', 'DISTRICT']

            # Find the first valid field index among the variations
            district_field_index = -1
            for name in district_field_names:
                index = active_layer.fields().indexOf(name)
                if index != -1:
                    district_field_index = index
                    break

            # Check if a valid field index is found
            if district_field_index != -1:
                # Get unique district values from the layer
                district_values = active_layer.uniqueValues(district_field_index)

                # Populate the combo box with district names
                self.district_combo_box.addItems(sorted(district_values))
            else:
                print("No valid district field found in the layer.")

    def update_shapefile_path(self, layer_path):
        self.shapefile_path_label = self.findChild(QtWidgets.QLabel, 'shapefile_path_label')
        if self.shapefile_path_label:
            self.shapefile_path_label.setText(layer_path)
        else:
            print("Error: shapefile_path_label not found.")

    def on_extract_button_clicked(self):
        # Get the district name from the QLineEdit
        # district_name = self.district_line_edit.text()
        # Get the selected district from the combo box
        selected_district = self.district_combo_box.currentText()

        # Get the active layer
        active_layer = iface.activeLayer()

        # Check if a district name is entered
        if not selected_district:
            QtWidgets.QMessageBox.critical(self, 'Error', 'Please select a district name.')
            return

        # Check if a layer is selected
        if not active_layer:
            QtWidgets.QMessageBox.critical(self, 'Error', 'Please load a shapefile layer.')
            return

        # Call the function to extract and save the district map
        extract_district_map(selected_district, active_layer)
        # Optionally, you can show a message to indicate success
        QtWidgets.QMessageBox.information(self, 'Success', f'Map for {selected_district} extracted and saved.')

        # Close the dialog
        self.accept()
