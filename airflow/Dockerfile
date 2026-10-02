# Custom Airflow image with ShippingDataPipeline dependencies.
#
# Build:
#   cd airflow
#   podman build -t shipping-airflow:latest .
#
# Then set `image: shipping-airflow:latest` in docker-compose.yml
# and remove the `_PIP_ADDITIONAL_REQUIREMENTS` line.

FROM apache/airflow:3.0.6

# Install project dependencies as the airflow user
USER airflow
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Switch back to root for any further system-level changes
USER root