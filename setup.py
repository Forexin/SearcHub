from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="data-aggregator",
    version="1.0.0",
    author="[您的名字]",
    author_email="[您的邮箱]",
    description="一个基于 FastAPI 的数据聚合搜索系统",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/YOUR_USERNAME/data-aggregator",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: FastAPI",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "data-aggregator=main:main",
        ],
    },
    package_data={
        "": [
            "frontend/templates/*.html",
            "frontend/templates/components/*.html",
            "frontend/templates/pages/*.html",
            "frontend/static/css/*.css",
            "frontend/static/js/*.js",
            "config/*.yaml",
            "plugins/example/**/*",
        ],
    },
    data_files=[
        ("", ["LICENSE", "README.md", "requirements.txt"]),
        ("scripts", ["install.sh", "manage.sh"]),
    ],
) 