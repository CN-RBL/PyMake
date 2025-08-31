from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize("*.pyx", nthreads=256, annotate=True),
)
