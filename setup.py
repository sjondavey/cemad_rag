from setuptools import setup, find_packages


setup(
    name='cemad_rag',
    version='0.5.3',
    author='SJon',
    url='https://github.com/sjondavey/cemad_rag',
    license='LICENSE.txt',
    description='A specific application package utilizing regulations_rag.',
    long_description=open('README.md').read(),
    install_requires=[
        # Assuming regulations_rag is hosted on GitHub and not available on PyPI
        'regulations_rag @ git+https://github.com/sjondavey/regulations_rag.git#egg=regulations_rag',
        # Add other dependencies here
    ],
)

# pip uninstall "git+https://github.com/sjondavey/regulations_rag.git#egg=regulations_rag"
# pip install -U "git+https://github.com/sjondavey/regulations_rag.git#egg=regulations_rag"