from generators import SolidColorGenerator, CheckerboardGenerator
from noises import WorleyNoiseGenerator, WhiteNoiseGenerator, PerlinNoiseGenerator

from modifiers import NoModifier, BrightnessModifier, OneMinus

# Maps for active(usable) generator and modifiers
# Used in NoiseGenApp

GENERATORS = {
    "Solid Color": SolidColorGenerator,
    "Checkerboard": CheckerboardGenerator,
    "WhiteNoise": WhiteNoiseGenerator,
    "WorleyNoise": WorleyNoiseGenerator,
    "PerlinNoise": PerlinNoiseGenerator,
}

MODIFIERS = {
    "None": NoModifier,
    "Brightness": BrightnessModifier,
    "OneMinus": OneMinus,
}