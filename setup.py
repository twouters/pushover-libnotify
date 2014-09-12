from setuptools import setup

setup(
    name="pushover-libnotify",
    version="0.1.dev1",
    install_requires=[
        "configparser",
        "requests",
        "pyxdg",
        "notify2",
        "websocket-client",
        "pillow",
        ],
    description="Pushover client that use libnotify to show notifications",
    author="Thomas Wouters",
    author_email="thomaswouters@gmail.com",
    license="GPLv3",
    keywords="pushover client libnotify",
    url="https://github.com/twouters/pushover-libnotify",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: Linux",
        "Development Status :: 3 - Alpha",
        "Natural Language :: English",
        ],
    packages=["pushover-libnotify"],
    )
