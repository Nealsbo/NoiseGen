import math
import numpy as np
from PIL import Image

from base import NoiseGenerator


    
class WhiteNoiseGenerator(NoiseGenerator):
    def __init__(self):
        self.data = None

    def get_ui_schema(self):
        sizes = [64, 128, 256, 512, 1024, 2048, 4096]
        return {
            "size": {"type": "choise", "label": "Size", "default": 512, "options": sizes},
            "colored": {"type": "bool", "label": "IsColored", "default": False},
        }
        
    def generate(self, params):
        self.size = params["size"]
        self.colored = params["colored"]
        if self.colored:
            self.data = np.random.randint(0, 255, (self.size, self.size, 3), dtype=np.uint8)
        else:
            temp = np.random.randint(0, 255, (self.size, self.size, 3), dtype=np.uint8)
            self.data = np.stack((temp, temp, temp), axis=-1)
        return self.data

    def get_data(self):
        return self.data

    def to_image(self):
        raise NotImplementedError



# TODO: rewrite to cell based algo
# fix(use) tiling
class WorleyNoiseGenerator(NoiseGenerator):
    def __init__(self):
        self.F1 = None
        self.F2 = None
        self.data = None
        self.points = None
    
    def get_ui_schema(self):
        sizes = [64, 128, 256, 512, 1024, 2048, 4096]
        return {
            "size": {"type": "choise", "label": "Size", "default": 512, "options": sizes},
            "num_points": {"type": "int", "label": "Points", "default": 16, "min": 2, "max": 64},
            "seed": {"type": "int", "label": "Seed", "default": 1},
            "tileable": {"type": "bool", "label": "Tiling", "default": False},
        }

    def _generate_points(self):
        rng = np.random.RandomState(self.seed)

        points = rng.rand(self.num_points, 2)
        points[:, 0] *= self.size
        points[:, 1] *= self.size

        return points

    def generate(self, params):
        self.size = params["size"]
        self.num_points = params["num_points"]
        self.seed = params["seed"]
        self.tileable = params["tileable"]

        points = self._generate_points()
        self.points = points
        self.data = np.ndarray([self.size, self.size], dtype=np.uint8)
        self.data = np.full((self.size, self.size, 3), fill_value=0, dtype=np.uint8)

        for y in range(0, self.size):
            for x in range(0, self.size):
                dist = float(self.size)
                for d in range(0, self.num_points):
                    dx = (x - self.points[d][0])
                    dy = (y - self.points[d][1])
                    tmp = math.sqrt(dx * dx + dy * dy)
                    dist = min(dist, tmp)
                val = np.clip(dist*3, 0, 255)
                self.data[x][y] = (val, val, val)
        
        return self.data

    def get_data(self):
        return self.data
    
    def to_image(self):
        return Image.fromarray(self.data)



# TODO: implementation
class PerlinNoise:
    def __init__(self):
        pass
        
    def generate(self, params):
        raise NotImplementedError

    def get_data(self):
        raise NotImplementedError
