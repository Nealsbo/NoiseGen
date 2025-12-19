from base import NoiseGenerator
import numpy as np



class SolidColorGenerator(NoiseGenerator):
    def get_ui_schema(self):
        sizes = [64, 128, 256, 512, 1024, 2048, 4096]
        return {
            "size": {"type": "choise", "label": "Size", "default": 512, "options": sizes},
            "color": {"type": "color", "label": "Color", "default": (0, 0, 0)}
        }

    def generate(self, params: dict) -> np.ndarray:
        size = params["size"]
        r, g, b = params["color"]
        return np.full((size, size, 3), [r, g, b], dtype=np.uint8)



class CheckerboardGenerator(NoiseGenerator):
    def get_ui_schema(self):
        sizes = [64, 128, 256, 512, 1024, 2048, 4096]
        return {
            "size": {"type": "choise", "label": "Size", "default": 512, "options": sizes},
            "cell_size": {"type": "int", "label": "Cell size", "default": 16, "min": 1, "max": 512},
            "color1": {"type": "color", "label": "Background color", "default": (255, 255, 255)},
            "color2": {"type": "color", "label": "Cell color", "default": (0, 0, 0)}
        }

    def generate(self, params: dict) -> np.ndarray:
        size = params["size"]
        cell = params["cell_size"]
        img = np.full((size, size, 3), params["color1"], dtype=np.uint8)
        for y in range(0, size, cell):
            for x in range(0, size, cell):
                if ((x // cell) + (y // cell)) % 2:
                    y2, x2 = min(y + cell, size), min(x + cell, size)
                    img[y:y2, x:x2] = params["color2"]
        return img


# TODO: Fix using direction of gradient
class GradientGenerator(NoiseGenerator):
    def get_ui_schema(self):
        sizes = [64, 128, 256, 512, 1024, 2048, 4096]
        options = ["Left->Right", "Right->Left", "Top->Bottom", "Bottom->Top"]
        return {
            "size": {"type": "choise", "label": "Size", "default": 512, "options": sizes},
            "direction": {"type": "list", "label": "Direction", "default": options[0], "options": options},
            "color1": {"type": "color", "label": "Color 1", "default": (255, 255, 255)},
            "color2": {"type": "color", "label": "Color 2", "default": (0, 0, 0)},
        }

    def generate(self, params: dict) -> np.ndarray:
        size = params["size"]
        r1, g1, b1 = params["color1"]
        r2, g2, b2 = params["color2"]
        dir = params["direction"]
        rrange = np.linspace(r1, r2, size, dtype=np.uint8)
        grange = np.linspace(g1, g2, size, dtype=np.uint8)
        brange = np.linspace(b1, b2, size, dtype=np.uint8)
        color_line = np.stack((rrange, grange, brange), axis=-1)
        print(color_line.shape)
        return np.full((size, size, 3), color_line, dtype=np.uint8)

