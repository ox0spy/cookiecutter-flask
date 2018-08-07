import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="{{cookiecutter.project_name}}",
    version="{{cookiecutter.project_version}}",
    author="{{cookiecutter.author}}",
    author_email="{{cookiecutter.email}}",
    description="{{cookiecutter.project_short_description}}",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/{{cookiecutter.author}}/{{cookiecutter.project_name}}",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
