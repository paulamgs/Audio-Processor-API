# The devcontainer should use the developer target and run as root with podman
# or docker with user namespaces.
ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION} as developer

# Set up a virtual environment and put it in PATH
RUN python -m venv /venv
ENV PATH=/venv/bin:$PATH

# The build stage installs the context into the venv
FROM developer as build
COPY . /context
WORKDIR /context
RUN pip install -e .

# The runtime stage copies the built venv into a slim runtime container
FROM python:${PYTHON_VERSION}-slim as runtime
# Copy the virtual environment from the build stage
COPY --from=build /venv/ /venv/
ENV PATH=/venv/bin:$PATH

# Change this entrypoint to run the FastAPI app
ENTRYPOINT ["uvicorn"]
CMD ["audio_processor.main:app", "--host", "0.0.0.0", "--port", "8000"]