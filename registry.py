from generators import SolidColorGenerator, CheckerboardGenerator, GradientGenerator
from noises import WorleyNoiseGenerator, WhiteNoiseGenerator, PerlinNoiseGenerator

from modifiers import NoModifier, BrightnessModifier, OneMinus, PowerOfX

# Maps for active(usable) generator and modifiers
# Used in NoiseGenApp

GENERATORS = {
    "Solid Color":  SolidColorGenerator,
    "Checkerboard": CheckerboardGenerator,
    "Gradient":     GradientGenerator,
    "WhiteNoise":   WhiteNoiseGenerator,
    "WorleyNoise":  WorleyNoiseGenerator,
    "PerlinNoise":  PerlinNoiseGenerator,
}

MODIFIERS = {
    "None":       NoModifier,
    "Brightness": BrightnessModifier,
    "OneMinus":   OneMinus,
    "PowerOfX":   PowerOfX,
}