from setuptools import setup
from setuptools import find_packages

setup(
    name="tastypie-user-session",
    version="0.2",
    packages=find_packages(),
    author="Tudor Prodan",
    author_email="tudor.prodan@gmail.com",
    description="User sessions on top of Tastypie, plus Facebook auth",
    long_description="",
    license="MIT",
    keywords="tastypie session authentication facebook",
    url="https://github.com/tudorprodan/tastypie_user_session/",
    install_requires=(
        "django_tastypie",
        "django"
    ),
    requires=(
        "django_tastypie",
        "django"
    ),
)
