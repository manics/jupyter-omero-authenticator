import setuptools

setuptools.setup(
    name='jupyter-omero-authenticator',
    version='0.0.1',
    url='https://github.com/manics/jupyter-omero-authenticator',
    author='Simon Li',
    license='MIT',
    description='Jupyterhub OMERO authenticator',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    data_files=[
        ('share/jupyterhub/templates/omero_authenticator/', [
            'jupyter_omero_authenticator/templates/omerologin.html']),
    ],
    install_requires=[
        'jupyterhub',
        'omero-py>=5.6.dev9',
    ],
    python_requires='>=3.5',
    classifiers=[
        'Framework :: Jupyter',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering',
    ],
    zip_safe=False
)
