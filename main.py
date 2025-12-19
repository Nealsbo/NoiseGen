import sys
import numpy as np

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton, QSlider, QFormLayout, QColorDialog,
    QLineEdit, QGroupBox, QMessageBox, QSpinBox, QDoubleSpinBox, QFrame, QCheckBox
)
from PyQt6.QtGui import QPixmap, QColor, QImage
from PyQt6.QtCore import Qt

from registry import GENERATORS, MODIFIERS

################
#
#  TODO:
#    -> Remove fixed numers
#    -> Implement set of modifiers
#    ---> clamp(min, max)
#    ---> colormap
#
################



class NoiseGenApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Noise Gen")
        self.setGeometry(100, 100, 1280, 720)
        self.scale_percent = 100
        self.current_qimage = None
        self.last_gen_instance = None

        self.generator_classes = GENERATORS
        self.modifier_classes = MODIFIERS

        self.generator_param_widgets = {}
        self.modifier_param_widgets = {}

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Left panel (view)
        self.image_label = QLabel()
        self.image_label.setMinimumSize(256, 256)
        self.image_label.setMaximumSize(1024, 1024)
        self.image_label.setStyleSheet("background-color: #1f1f1f; border: 1px solid #ccc;")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        scale_layout = QHBoxLayout()
        self.scale_slider = QSlider(Qt.Orientation.Horizontal)
        self.scale_slider.setRange(10, 400)
        self.scale_slider.setValue(100)
        self.scale_slider.valueChanged.connect(self.on_slider_changed)

        self.scale_edit = QLineEdit("100")
        self.scale_edit.setFixedWidth(60)
        self.scale_edit.editingFinished.connect(self.on_edit_finished)

        scale_layout.addWidget(QLabel("Scale (%):"))
        scale_layout.addWidget(self.scale_slider)
        scale_layout.addWidget(self.scale_edit)

        left_layout = QVBoxLayout()
        left_layout.addWidget(self.image_label)
        left_layout.addLayout(scale_layout)

        # Right panel (control)
        right_layout = QVBoxLayout()

        ## Generator
        self.gen_combo = QComboBox()
        self.gen_combo.addItems(self.generator_classes.keys())
        self.gen_combo.currentTextChanged.connect(self.on_generator_changed)

        gen_group = QGroupBox("Generator")
        gen_group.setLayout(QVBoxLayout())
        gen_group.layout().addWidget(self.gen_combo)

        self.gen_params_group = QGroupBox("Generator Parameters")
        self.gen_params_layout = QFormLayout()
        self.gen_params_group.setLayout(self.gen_params_layout)

        ## Modifier
        self.mod_combo = QComboBox()
        self.mod_combo.addItems(self.modifier_classes.keys())
        self.mod_combo.currentTextChanged.connect(self.on_modifier_changed)

        mod_group = QGroupBox("Modifiers")
        mod_group.setLayout(QVBoxLayout())
        mod_group.layout().addWidget(self.mod_combo)

        self.mod_params_group = QGroupBox("Modifier Parameters")
        self.mod_params_layout = QFormLayout()
        self.mod_params_group.setLayout(self.mod_params_layout)

        ## Buttons
        self.btn_generate = QPushButton("Generate")
        self.btn_modify = QPushButton("Apply Modifier")
        self.btn_save = QPushButton("Save Image")
        self.btn_generate.clicked.connect(self.generate_image)
        self.btn_modify.clicked.connect(self.apply_modifier)
        self.btn_save.clicked.connect(self.save_image)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_generate)
        btn_layout.addWidget(self.btn_modify)
        btn_layout.addWidget(self.btn_save)

        right_layout.addWidget(gen_group)
        right_layout.addWidget(self.gen_params_group)
        line = QFrame() 
        line.setFrameShape(QFrame.Shape.HLine)
        right_layout.addWidget(line)
        right_layout.addWidget(mod_group)
        right_layout.addWidget(self.mod_params_group)
        right_layout.addStretch()
        right_layout.addLayout(btn_layout)

        main_layout.addLayout(left_layout, 3)
        main_layout.addLayout(right_layout, 2)

        # Update parameters
        self.on_generator_changed(self.gen_combo.currentText())
        self.on_modifier_changed(self.mod_combo.currentText())

    def on_generator_changed(self, name):
        cls = self.generator_classes[name]
        instance = cls()
        schema = instance.get_ui_schema()
        self.build_ui_from_schema(schema, self.gen_params_layout, self.generator_param_widgets)

    def on_modifier_changed(self, name):
        cls = self.modifier_classes[name]
        instance = cls()
        schema = instance.get_ui_schema()
        self.build_ui_from_schema(schema, self.mod_params_layout, self.modifier_param_widgets)

    # Build parameters for generator or modifier
    def build_ui_from_schema(self, schema, layout, widget_store):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        widget_store.clear()

        for param_name, desc in schema.items():
            label = desc.get("label", param_name)
            ptype = desc["type"]
            default = desc["default"]

            if "options" in desc:
                options = desc["options"]

            if ptype == "int":
                w = QSpinBox()
                w.setRange(desc.get("min", 0), desc.get("max", 100))
                w.setValue(default)
            elif ptype == "float":
                w = QDoubleSpinBox()
                w.setRange(desc.get("min", 0.0), desc.get("max", 100.0))
                w.setSingleStep(desc.get("step", 0.1))
                w.setValue(default)
            elif ptype == "color":
                w = QPushButton("Choose")
                w.selected_color = QColor(*default)
                w.setStyleSheet(f"background-color: {w.selected_color.name()};")
                w.clicked.connect(lambda _, n=param_name: self.pick_color(w, widget_store, n))
                widget_store[param_name + "_color"] = w.selected_color
            elif ptype == "bool":
                w = QCheckBox()
                w.setChecked(default)
            elif ptype == "list":
                w = QComboBox()
                w.addItems(options)
            else:
                w = QLineEdit(str(default))

            layout.addRow(f"{label}:", w)
            widget_store[param_name] = w

    def pick_color(self, button, store, param_name):
        color = QColorDialog.getColor(button.selected_color, self, "Color")
        if color.isValid():
            button.selected_color = color
            store[param_name + "_color"] = color
            button.setStyleSheet(f"background-color: {color.name()};")

    def collect_params(self, widget_store):
        params = {}
        for name, widget in widget_store.items():
            if name.endswith("_color"):
                continue
            if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                params[name] = widget.value()
            elif isinstance(widget, QPushButton) and hasattr(widget, "selected_color"):
                qcolor = widget_store.get(name + "_color", QColor(0,0,0))
                params[name] = (qcolor.red(), qcolor.green(), qcolor.blue())
            elif isinstance(widget, QCheckBox):
                params[name] = widget.isChecked()
            elif isinstance(widget, QComboBox):
                params[name] = widget.currentText()
            else:
                try:
                    params[name] = eval(widget.text())
                except:
                    params[name] = widget.text()
        return params

    def generate_image(self):
        gen_name = self.gen_combo.currentText()
        gen_cls = self.generator_classes[gen_name]
        gen_params = self.collect_params(self.generator_param_widgets)
        if(self.last_gen_instance is None or not isinstance(self.last_gen_instance, type(gen_cls))):
            self.last_gen_instance = gen_cls()
        self.np_img = self.last_gen_instance.generate(gen_params)

        # ndarray to QImage
        h, w = self.np_img.shape[:2]
        self.current_qimage = QImage(self.np_img.data, w, h, 3 * w, QImage.Format.Format_RGB888).copy()
        self.update_view()

    def apply_modifier(self):
        mod_name = self.mod_combo.currentText()
        mod_cls = self.modifier_classes[mod_name]
        mod_params = self.collect_params(self.modifier_param_widgets)
        mod_instance = mod_cls()
        
        self.np_img = mod_instance.apply(self.np_img, mod_params)
        h, w = self.np_img.shape[:2]
        self.current_qimage = QImage(self.np_img.data, w, h, 3 * w, QImage.Format.Format_RGB888).copy()
        self.update_view()

    def update_view(self):
        if self.current_qimage is None:
            return
        
        scaled = self.current_qimage.scaled(
            int(self.current_qimage.width() * self.scale_percent / 100),
            int(self.current_qimage.height() * self.scale_percent / 100),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.image_label.setPixmap(QPixmap.fromImage(scaled))

    def on_slider_changed(self, value):
        self.scale_percent = value
        self.scale_edit.setText(str(value))
        self.update_view()

    def on_edit_finished(self):
        try:
            val = int(self.scale_edit.text())
            if 10 <= val <= 400:
                self.scale_slider.setValue(val)
                self.scale_percent = val
                self.update_view()
            else:
                raise ValueError
        except:
            self.scale_edit.setText(str(self.scale_percent))
            QMessageBox.warning(self, "Error", "Only number from 10 to 800")

    def save_image(self):
        if not self.current_qimage:
            return
        from PyQt6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getSaveFileName(self, "Save", "", "PNG (*.png)")
        if path:
            if not path.endswith(".png"):
                path += ".png"
            self.current_qimage.save(path, "PNG")



# Entry point
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NoiseGenApp()
    window.show()
    sys.exit(app.exec())