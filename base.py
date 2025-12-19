from abc import ABC, abstractmethod
import numpy as np
from PyQt6.QtGui import QImage



class NoiseGenerator(ABC):
    @abstractmethod
    def generate(self) -> np.ndarray:
        pass

    @abstractmethod
    def get_ui_schema(self) -> dict:
        """
        Should return dict for parameter constructor 
        {
            "param_name1": {
                "type": "int" | "float" | "color" | "bool" | "choice",
                "label": "Name",
                "default": ...,
                "min"/"max"/"options" (optional)
            },
            "param_name2": ...
        }
        """
        pass

    def get_data(self) -> np.ndarray:
        return self.data

    def to_qimage(self) -> QImage:
        data = self.generate()
        h, w = data.shape[:2]
        return QImage(data.data, w, h, 3 * w, QImage.Format.Format_RGB888).copy()



class NoiseModifier(ABC):
    @abstractmethod
    def apply(self, image: np.ndarray, params: dict) -> np.ndarray:
        pass

    @abstractmethod
    def get_ui_schema(self) -> dict:
        pass