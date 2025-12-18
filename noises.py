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
        self.params = None
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
        if self.params == params:
            print("Noise already exist with same parameters, no job to generate")
            return self.data
        else:
            print(self.params)
            print(params)
            print('========')
            self.params = params

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



# TODO: Fix tiling
class PerlinNoiseGenerator(NoiseGenerator):
    def __init__(self):
        self.size = 0
        self.grid_size = 0
        self.tablesize = 256

        self.data = None
        self.vecs = None
        self.params = None

    def get_ui_schema(self):
        sizes = [64, 128, 256, 512, 1024, 2048, 4096]

        return {
            "size": {"type": "choise", "label": "Size", "default": 512, "options": sizes},
            "grid_size": {"type": "int", "label": "Grid size", "default": 16, "min": 2, "max": 256},
            "octaves": {"type": "int", "label": "Octaves", "default": 4, "min": 1, "max": 8},
            "persistance": {"type": "float", "label": "Persistance", "default": 1.0},
            "seed": {"type": "int", "label": "Seed", "default": 1},
            "tileable": {"type": "bool", "label": "Tiling", "default": False},
        }

    def _dot(self, x1, y1, x2, y2):
        return x1*x2 + y1*y2

    def _nrm(self, x, y):
        len = math.sqrt(x*x + y*y)
        xn = x / len
        yn = y / len
        return (xn, yn)

    def _fade(self, v1, v2):
        x = 6 * math.pow(v1, 5.0) - 15 * math.pow(v1, 4.0) + 10 *  math.pow(v1, 3.0)
        y = 6 * math.pow(v2, 5.0) - 15 * math.pow(v2, 4.0) + 10 *  math.pow(v2, 3.0)
        return (x, y)

    def _lerp(self, t, a1, a2):
        return a1 + t * (a2 - a1)

    def _generate_vectors(self):
        step = math.pi * 2.0 / self.tablesize
        angles = np.arange(self.tablesize) * step
        self.grads = np.stack((np.cos(angles), np.sin(angles)), axis=1)
        self.table = np.arange(self.tablesize, dtype=int)
        self.table = np.concatenate((self.table, self.table))
        np.random.shuffle(self.table)

    def _get_vec(self, x, y):
        index = self.table[self.table[x] + y]
        return self.grads[index]

    def noise(self, x, y):
        x0 = int(np.floor(x)) % 256
        y0 = int(np.floor(y)) % 256
        x1 = (x0 + 1) % 256
        y1 = (y0 + 1) % 256

        sx = x - np.floor(x)
        sy = y - np.floor(y)

        # corner vectors of pixel grid cell
        v00 = self._get_vec(int(x0), int(y0))
        v01 = self._get_vec(int(x0), int(y1))
        v10 = self._get_vec(int(x1), int(y0))
        v11 = self._get_vec(int(x1), int(y1))

        # vector to pixel in grid cell
        d00 = (sx, sy)
        d01 = (sx, sy - 1)
        d10 = (sx - 1, sy)
        d11 = (sx - 1, sy - 1)

        h0 = self._dot(d00[0], d00[1], v00[0], v00[1])
        h1 = self._dot(d01[0], d01[1], v01[0], v01[1])
        h2 = self._dot(d10[0], d10[1], v10[0], v10[1])
        h3 = self._dot(d11[0], d11[1], v11[0], v11[1])

        u, v = self._fade(sx, sy)

        l1 = self._lerp(u, h0, h2)
        l2 = self._lerp(u, h1, h3)

        res = self._lerp(v, l1, l2)
        return res

    def octave_noise(self, x, y):
        total = 0.0
        amplitude = self.persistance
        frequency = 1.0 / self.size * self.grid_size

        for i in range(self.octaves):
            total += amplitude * self.noise(x * frequency, y * frequency)
            amplitude *= 0.5
            frequency *= 2.0

        return total

    def generate(self, params):
        self.size = params["size"]
        self.grid_size = params["grid_size"]
        self.octaves = params["octaves"]
        self.persistance = params["persistance"]
        self.seed = params["seed"]
        self.tileable = params["tileable"]

        np.random.seed(self.seed)

        self._generate_vectors()
        noise_data = np.zeros((self.size, self.size))
        u8noise_data = np.zeros((self.size, self.size), dtype=np.uint8)

        for y in range(self.size):
            for x in range(self.size):
                val = self.octave_noise(x, y)
                #val = (val + 1.0) * 0.5
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
