from setuptools import setup, find_packages

setup(
    name="mediawebcore",
    version="0.1.0",
    description="A reusable real-time media streaming Flask+SocketIO platform",
    author="Your Name",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'mediawebcore': ['templates/*.html'],
    },
    install_requires=[
        "flask",
        "flask-socketio",
        "opencv-python",
        "eventlet",
        "numpy",
    ],
    python_requires=">=3.8",
)
