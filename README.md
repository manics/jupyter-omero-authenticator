# Jupyter OMERO Authenticator

Use [OMERO](https://www.openmicroscopy.org/omero/) to authenticate with [JupyterHub](https://jupyter.org/hub).

## Example `jupyterhub_config.py`
```
c.JupyterHub.authenticator_class = 'jupyter_omero_authenticator.OmeroAuthenticator'
c.OmeroAuthenticator.omero_host = 'omero.example.org'
```