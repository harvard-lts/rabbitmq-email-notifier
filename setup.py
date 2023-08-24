import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lts-rabbitmqemailnotifier",
    version="0.0.6",
    author="Chip Goines",
    author_email="chip_goines@harvard.edu",
    description="A set of utilities for placing a message " +
                "onto a queue for an emailer listener to receive",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/harvard-lts/rabbitmq-email-notifier",
    packages=setuptools.find_packages(),
    install_requires=[
        'celery==5.2.7',
        'certifi==2023.7.22',
        'coverage==7.2.6',
        'iniconfig==2.0.0',
        'lxml==4.9.2',
        'opentelemetry-api==1.19.0',
        'opentelemetry-sdk==1.19.0',
        'opentelemetry-exporter-jaeger==1.19.0',
        'opentelemetry-exporter-otlp-proto-grpc==1.19.0',
        'opentelemetry-semantic-conventions==0.40b0',
        'packaging==23.1',
        'pika==1.3.2',
        'pluggy==1.0.0',
        'project-paths==1.1.1',
        'pytest==7.3.1',
        'pytest-mock==3.10.0',
        'python-dotenv==1.0.0',
        'requests==2.31.0',
        'requests-mock==1.10.0',
        'retrying==1.3.4',
        'toml==0.10.2',
        'tomli==2.0.1',
        'twine==4.0.2',
        'urllib3==2.0.2'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    include_package_data=True,
    package_data={
        # Include all *.json files in any package
        "": ["*.json"],
    }
)
