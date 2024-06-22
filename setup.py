from distutils.core import setup


setup(
    name="vttermproxy",
    version="1.0.0",
    description="VT-100 Proxy Host",
    author="DragonMinded",
    license="Public Domain",
    packages=[
        "proxy",
    ],
    install_requires=[
        req for req in open("requirements.txt").read().split("\n") if len(req) > 0
    ],
    python_requires=">3.8",
    entry_points={
        "console_scripts": [
            "vttermproxy = proxy.__main__:cli",
        ],
    },
)
