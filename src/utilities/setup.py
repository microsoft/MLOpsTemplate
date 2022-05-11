import setuptools
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='monitoring',
    version='0.0.2',
    author='James Nguyen; Nicole Serafino',
    author_email='janguy@microsoft.com;nserafino@microsoft.com',
    description='Testing installation of Package',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/microsoft/MLOpsTemplate/tree/monitoring-main/src/utilities',
    project_urls = {
        "Bug Tracker": "https://github.com/microsoft/MLOpsTemplate/issues"
    },
    license='MIT',
    packages=['monitoring'],
    install_requires=['azure-identity==1.9.0','azure-mgmt-kusto==2.2.0','azure-kusto-data==3.1.2','azure-kusto-ingest==3.1.2','jupyter-dash==0.4.2'],
)
