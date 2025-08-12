"""
Setup script.
"""

from setuptools import find_packages, setup

if __name__ == "__main__":
    with open("README.rst", "r", encoding="utf-8") as readme:
        setup(
            name="cfn-sync",
            use_scm_version=True,
            description="Deploy CloudFormation stacks synchronously and watch the events",
            author="Sam Jarrett",
            author_email="sam@samjarrett.com.au",
            url="https://github.com/samjarrett/cfn-sync",
            long_description=readme.read(),
            classifiers=[
                "License :: OSI Approved :: MIT License",
                "Programming Language :: Python",
                "Programming Language :: Python :: 3",
                "Programming Language :: Python :: 3.9",
                "Programming Language :: Python :: 3.10",
                "Programming Language :: Python :: 3.11",
                "Programming Language :: Python :: 3.12",
                "Programming Language :: Python :: 3.13",
            ],
            packages=find_packages(exclude=["tests"]),
            include_package_data=True,
            package_data={"cfn_sync": ["py.typed"]},
            entry_points={"console_scripts": ["cfn-sync = cfn_sync:main"]},
            python_requires=">=3.9",
            setup_requires=["setuptools >= 18.0", "setuptools_scm"],
            install_requires=["boto3>=1.12.0"],
            test_suite="tests",
        )
