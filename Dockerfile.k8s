FROM jupyterhub/k8s-hub:0.9.0-alpha.1.095.3e95dc3
# https://hub.docker.com/layers/jupyterhub/k8s-hub/0.9.0-alpha.1.095.3e95dc3/images/sha256-711e9eb3b3c13ff072cd13b160bf68fbb2c7bf69c649b2a8abaed7130dc0ae0c
# 12/17/2019 at 7:06 am

USER root
RUN python3 -mpip install https://github.com/ome/zeroc-ice-ubuntu1804/releases/download/0.3.0/zeroc_ice-3.6.5-cp36-cp36m-linux_x86_64.whl

ADD . /jupyter-omero-authenticator/
RUN cd /jupyter-omero-authenticator && python3 -mpip install .

USER jovyan
