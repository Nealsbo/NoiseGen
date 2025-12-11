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



# TODO: fix(use) tiling
class WorleyNoiseGenerator(NoiseGenerator):
    def __init__(self):
        self.F1 = None
        self.F2 = None
        self.data = None
        self.points = None
        self.modes = {
            "F1" : (lambda f1, f2: f1),
            "F2" : (lambda f1, f2: f2),
            "F2 + F1" : (lambda f1, f2: f2 + f1),
            "F2 - F1" : (lambda f1, f2: f2 - f1),
            "F2 * F1" : (lambda f1, f2: f2 * f1), 
            "F2 / F1" : (lambda f1, f2: f2 / f1)
        }
    
    def get_ui_schema(self):
        sizes = [64, 128, 256, 512, 1024, 2048, 4096]

        return {
            "size": {"type": "choise", "label": "Size", "default": 512, "options": sizes},
            "grid_size": {"type": "int", "label": "Grid size", "default": 16, "min": 2, "max": 64},
            "seed": {"type": "int", "label": "Seed", "default": 1},
            "tileable": {"type": "bool", "label": "Tiling", "default": False},
            "mode" : {"type": "list", "label": "Result modes", "default": "F1", "options": self.modes.keys()},
        }

    def _generate_points(self):
        points = np.zeros((self.grid_size, self.grid_size, 2))
        for j in range(self.grid_size):
            for i in range(self.grid_size):
                x = np.random.random()
                y = np.random.random()
                points[i, j, 0] = x + i
                points[i, j, 1] = y + j
        self.points = points
    
    def _dist_square(self, x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1
        return math.sqrt(dx*dx + dy*dy)
    
    def _get_dists(self, x, y, n=2) -> np.array:
        dists = np.full(9, np.inf)

        cell_x = int(np.floor(x)) % self.grid_size
        cell_y = int(np.floor(y)) % self.grid_size
        
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                near_x = (cell_x + dx) % self.grid_size
                near_y = (cell_y + dy) % self.grid_size

                point_x, point_y = self.points[near_x, near_y]
                d_sq = self._dist_square(x, y, point_x, point_y)
                index = (dx + 1) * 3 + dy + 1
                dists[index] = d_sq

        dists = np.sort(dists)
        return dists

    def noise(self, x, y, n=2, scale=1.0, mode="F1"):
        scaled_x = x * (self.grid_size / self.size)
        scaled_y = y * (self.grid_size / self.size)

        distances = self._get_dists(scaled_x, scaled_y, n)
        #return distances[0]
        return self.modes[mode](distances[0], distances[1])

    def generate(self, params):
        self.size = params["size"]
        self.grid_size = params["grid_size"]
        self.seed = params["seed"]
        self.tileable = params["tileable"]
        self.mode = params["mode"]
        n = 2

        np.random.seed(self.seed)

        self._generate_points()
        noise_data = np.zeros((self.size, self.size))

        for y in range(0, self.size):
            for x in range(0, self.size):
                val = self.noise(x, y, n, mode=self.mode)
                noise_data[x, y] = val

        data_min = noise_data.min()
        data_max = noise_data.max()

        if data_max > data_min:
            noise_data = (noise_data - data_min) / (data_max - data_min)
        u8noise_data = (noise_data * 255).astype(np.uint8)
        self.data = np.stack((u8noise_data, u8noise_data, u8noise_data), axis=-1)
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
