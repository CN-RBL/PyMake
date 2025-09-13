from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize("pymake.pyx", nthreads=255, annotate=True)
)
setup(
    ext_modules=cythonize("lang.pyx", nthreads=255, annotate=True)
)

