# Dockerfile for binder

FROM sagemath/sagemath:latest

# Copy the contents of the repo in ${HOME}
COPY --chown=sage:sage . ${HOME}

# Install this package and dependencies
RUN sage -pip install .