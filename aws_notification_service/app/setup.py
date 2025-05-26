"""
aws_notification_service setup
"""
from setuptools import setup

requirements = [
    "boto3",
]

dev_requirements = [
    "pytest",
    "pytest-cov",
]

setup(
    name="aws_notification_service",
    packages=["aws_notification_service"],
    package_dir={"aws_notification_service": "src/aws_notification_service"},
    # Dependencies
    install_requires=requirements,
    extras_require={
        "dev": dev_requirements
    }
)
