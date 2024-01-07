from qgis.PyQt.QtCore import QObject, pyqtSignal
from qgis.core import QgsMapLayer
from qgis.utils import iface


class LayerAddedListener(QObject):
    layer_added = pyqtSignal(str)

    def __init__(self):
        super(LayerAddedListener, self).__init__()
        iface.currentLayerChanged.connect(self.on_layer_added)

    def on_layer_added(self, layer):
        if layer and layer.type() == QgsMapLayer.VectorLayer:
            self.layer_added.emit(layer.source())
