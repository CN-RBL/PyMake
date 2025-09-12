from setuptools import setup
from Cython.Build import cythonize

setup(
    #                                       INT_MAX
    ext_modules=cythonize("*.pyx", nthreads=2147483647, annotate=True, compiler_directives={
        "language_level": 3
    }
    )
)
