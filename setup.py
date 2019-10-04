import setuptools

setuptools.setup(
    name='jupyter-omero-authenticator',
    version='0.0.1',
    url='https://github.com/manics/jupyter-omero-authenticator',
    author='Simon Li',
    license='BSD 3-Clause',
    description='Jupyterhub OMERO authenticator',
    packages=setuptools.find_packages(),
    install_requires=['jupyterhub'],
    python_requires='>=3.5',
    classifiers=[
        'Framework :: Jupyter',
    ],
    zip_safe=False
)
