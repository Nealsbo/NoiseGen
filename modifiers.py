# modifiers.py

from base import NoiseModifier
import numpy as np



class NoModifier(NoiseModifier):
    def get_ui_schema(self):
        return {}

    def apply(self, image: np.ndarray, params: dict) -> np.ndarray:
        return image

class BrightnessModifier(NoiseModifier):
    def get_ui_schema(self):
        return {
            "value": {"type": "float", "label": "Brightness", "default": 1.0, "min": 0.0, "max": 3.0, "step": 0.1}
        }

    def apply(self, image: np.ndarray, params: dict) -> np.ndarray:
        return np.clip(image * params["value"], 0, 255).astype(np.uint8)
    


class OneMinus(NoiseModifier):
    def get_ui_schema(self):
        return {}
    
    def _one_minus(x):
        if type(x) == np.uint8:
            return 255-x
        else:
            raise NotImplementedError

    def apply(self, image: np.ndarray, params: dict) -> np.ndarray:
        fx = lambda x: 255-x
        return fx(image)



class PowerOfX(NoiseModifier):
    def get_ui_schema(self):
        return {
            "value": {"type": "float", "label": "Exponent", "default": 2.0, "min": 0.0, "max": 10.0, "step": 0.1}
        }

    def fx(self, x, y):
        xf = x / 255.0
        res = np.pow(xf, y) * 255
        return np.array(res).astype(np.uint8)

    def apply(self, image: np.ndarray, params: dict) -> np.ndarray:
        return self.fx(image, params["value"])