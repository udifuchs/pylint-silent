"""Test pylint-silent workflow."""
import os
import shutil
import filecmp
import multiprocessing
from contextlib import redirect_stdout
import unittest.mock
import runpy
from typing import Optional
import pytest
import pylint.lint


def run_pylint_silent(*args: str) -> Optional[int]:
    """Run pylint-silent as if it was an executable."""
    with unittest.mock.patch("sys.argv", ["", *args]):
        try:
            runpy.run_module("pylint_silent", run_name="__main__")
        except SystemExit as ex:
            return ex.code
        return None


class Context:  # pylint: disable=too-few-public-methods
    """Create context for running tests.
    This includes a temporary folder and pointers to all related file names."""
    def __init__(self, tmpdir: str) -> None:
        self.sample_filename = "tests/sample_1.py"
        self.sample_after_apply = "tests/sample_1_after_apply.py"

        # Check that input test files exsist.
        assert os.path.isfile(self.sample_filename)
        assert os.path.isfile(self.sample_after_apply)

        # Copy test files to temp folder
        sample_basename = os.path.basename(self.sample_filename)
        self.temp_sample_filename = os.path.join(tmpdir, sample_basename)
        shutil.copy(self.sample_filename, self.temp_sample_filename)

        sample_apply_basename = os.path.basename(self.sample_after_apply)
        self.temp_sample_after_apply = os.path.join(tmpdir, sample_apply_basename)
        shutil.copy(self.sample_after_apply, self.temp_sample_after_apply)

    def run_pylint(self, *args: str) -> Optional[int]:
        """Run pylint on our python test files."""
        pylint_opts = ((self.temp_sample_filename,
                        self.temp_sample_after_apply) + args,)
        proc = multiprocessing.Process(target=pylint.lint.Run, args=pylint_opts)
        proc.start()
        proc.join()
        return proc.exitcode

    def run_pylint_to_file(self, out_file: str) -> Optional[int]:
        """Run pylint on our python test files redirecting stdout to file."""
        with open(out_file, "w") as out, \
             redirect_stdout(out):
            return self.run_pylint()


@pytest.fixture(name="ctx")
def fixture_ctx(tmpdir: str) -> Context:
    """Create context fixure for running tests."""
    return Context(tmpdir)


def test_version_option() -> None:
    """Test --version option"""
    status = run_pylint_silent("--version")
    assert status == 0


def test_no_params() -> None:
    """Test exit error with no parameters."""
    status = run_pylint_silent()
    assert status == 1


def test_bad_params() -> None:
    """Test exit error with bad parameters."""
    status = run_pylint_silent("bad-param")
    assert status == 1


def test_apply(ctx: Context) -> None:
    """Test 'pylint-silent apply'."""
    # Run pylint on test files.
    pylint_output = ctx.temp_sample_filename + "lint"
    ctx.run_pylint_to_file(pylint_output)

    # Apply pylint-silent changed based on output from pylint.
    run_pylint_silent("apply", pylint_output)

    # Test that the expected python file was generated.
    assert filecmp.cmp(ctx.temp_sample_filename, ctx.sample_after_apply), \
        f"diff {ctx.temp_sample_filename} {ctx.sample_after_apply}"

    # Test that pylint is indeed silent now.
    exitcode = ctx.run_pylint("--disable=duplicate-code")
    assert exitcode == 0


def test_stats(ctx: Context) -> None:
    """Test that 'pylint-silent stats' have not changed."""
    sample_stats = ctx.temp_sample_filename + "_stats"
    with redirect_stdout(open(sample_stats, "w")):
        run_pylint_silent("stats", ctx.sample_after_apply)

    assert filecmp.cmp(sample_stats, ctx.sample_filename + "_stats"), \
        f"diff {sample_stats} {ctx.sample_filename + '_stats'}"


def test_reset(ctx: Context) -> None:
    """Test 'pylint-silent reset'.
    Remove all generated comments and test that we are back to the original code.
    """
    run_pylint_silent("reset", ctx.temp_sample_after_apply)

    assert filecmp.cmp(ctx.temp_sample_after_apply, ctx.sample_filename), \
        f"diff {ctx.temp_sample_filename} {ctx.sample_filename}"

    # Test reseting a clean file.
    run_pylint_silent("reset", ctx.temp_sample_after_apply)

    assert filecmp.cmp(ctx.temp_sample_after_apply, ctx.sample_filename), \
        f"diff {ctx.temp_sample_filename} {ctx.sample_filename}"
