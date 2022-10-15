from distutils.core import setup, Extension


def main():
    setup(name="magicautils",
          version="0.0.0",
          description="MagicaPixel's utils lib",
          author="DungyBug",
          author_email="",
          ext_modules=[Extension("magicautils", sources=["src/clamp.cpp", "src/lerp.cpp", "src/pixelutils.cpp", "src/canvas.cpp", "src/rendercanvases.cpp", "src/main.cpp"], extra_compile_args=["/std:c++20"])])


if __name__ == "__main__":
    main()
