# Jupyter OMERO Authenticator
[![Build Status](https://travis-ci.com/manics/jupyter-omero-authenticator.svg?branch=master)](https://travis-ci.com/manics/jupyter-omero-authenticator)
[![PyPI](https://img.shields.io/pypi/v/jupyter-omero-authenticator)](https://pypi.org/project/jupyter-omero-authenticator/)

Use [OMERO](https://www.openmicroscopy.org/omero/) to authenticate with [JupyterHub](https://jupyter.org/hub).

## Example

You are strongly recommended to enable auth_state persistence so that OMERO session-ids can be checked and refreshed.

`jupyterhub_config.py`:
```python
c.JupyterHub.authenticator_class = 'jupyter_omero_authenticator.OmeroAuthenticator'
c.OmeroAuthenticator.omero_host = 'omero.example.org'

# Pass OMERO_HOST OMERO_USER OMERO_SESSION environment variables
c.OmeroAuthenticator.export_omero_env = True

c.Authenticator.auth_refresh_age = 300
c.Authenticator.enable_auth_state = True
c.Authenticator.refresh_pre_spawn = True
```
```bash
export JUPYTERHUB_CRYPT_KEY=$(openssl rand -hex 32)
jupyterhub
```