"""Nox sessions for the Local LLM Service."""

import nox


@nox.session(python=["3.9"])
def test(session):
    """Run the test suite."""
    session.install("poetry")
    session.run("poetry", "install")
    session.run("pytest", "tests/", "-v")


@nox.session(python=["3.9"])
def lint(session):
    """Run the linter."""
    session.install("poetry")
    session.run("poetry", "install")
    session.run("pylint", "app/", "tests/")


@nox.session(python=["3.9"])
def type_check(session):
    """Run the type checker."""
    session.install("poetry")
    session.run("poetry", "install")
    session.run("mypy", "app/", "tests/")
