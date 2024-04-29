"""Test pylint-silent workflow."""
import os
import shutil
import filecmp
import multiprocessing
from contextlib import redirect_stdout
import unittest.mock
import runpy
from typing import Optional, Union
import pytest
import pylint.lint


def run_pylint_silent(*args: str) -> Union[int, str, None]:
    """Run pylint-silent as if it was an executable."""
    with unittest.mock.patch("sys.argv", ["", *args]):
        try:
            runpy.run_module("pylint_silent", run_name="__main__")
        except SystemExit as ex:
            return ex.code
        return None


# pylint: disable-next=too-few-public-methods,too-many-instance-attributes; silent
class Context:
    """Create context for running tests.
    This includes a temporary folder and pointers to all related file names."""
    def __init__(self, tmpdir: str) -> None:
        self.sample_filename = "tests/sAmple_1.py"
        self.sample_after_apply = "tests/sAmple_1_after_apply.py"
        self.sample_after_apply_mixed = "tests/sAmple_1_after_apply_mixed.py"
        self.sample_after_apply_w_sig = "tests/sAmple_1_after_apply_w_signature.py"
        self.sample2_filename = "tests/sample_2.py"
        self.sample2_after_reset = "tests/sample_2_after_reset.py"

        # Check that input test files exist.
        assert os.path.isfile(self.sample_filename)
        assert os.path.isfile(self.sample_after_apply)
        assert os.path.isfile(self.sample_after_apply_mixed)
        assert os.path.isfile(self.sample_after_apply_w_sig)
        assert os.path.isfile(self.sample2_filename)
        assert os.path.isfile(self.sample2_after_reset)

        # Copy test files to temp folder
        sample_basename = os.path.basename(self.sample_filename)
        sample2_basename = os.path.basename(self.sample2_filename)
        self.temp_sample_filename = os.path.join(tmpdir, sample_basename)
        shutil.copy(self.sample_filename, self.temp_sample_filename)
        self.temp_sample2_filename = os.path.join(tmpdir, sample2_basename)
        self.temp_sample2_again_filename = os.path.join(
            tmpdir, f"again_{sample2_basename}"
        )
        shutil.copy(self.sample2_filename, self.temp_sample2_filename)
        shutil.copy(self.sample2_filename, self.temp_sample2_again_filename)

        sample_apply_basename = os.path.basename(self.sample_after_apply)
        sample_apply_w_sig_basename = os.path.basename(self.sample_after_apply_w_sig)
        self.temp_sample_after_apply = os.path.join(tmpdir, sample_apply_basename)
        self.temp_sample_after_apply_w_sig = os.path.join(
            tmpdir, sample_apply_w_sig_basename
        )
        shutil.copy(self.sample_after_apply, self.temp_sample_after_apply)
        shutil.copy(self.sample_after_apply_w_sig, self.temp_sample_after_apply_w_sig)

    def run_pylint(self, *args: str) -> Optional[int]:
        """Run pylint on our python test files."""
        pylint_opts = (self.temp_sample_filename, self.temp_sample_after_apply, *args)
        proc = multiprocessing.Process(target=pylint.lint.Run, args=(pylint_opts,))
        proc.start()
        proc.join()
        return proc.exitcode

    def run_pylint_to_file(self, out_file: str) -> Optional[int]:
        """Run pylint on our python test files redirecting stdout to file."""
        with open(out_file, "w", encoding="utf-8") as out, \
             redirect_stdout(out):
            return self.run_pylint("--max-module-lines=10")


def assert_files_equal(file_1: str, file_2: str) -> None:
    """Check that both file are the same and have the same permissions."""
    assert filecmp.cmp(file_1, file_2), f"diff {file_1} {file_2}"
    f1_mode = os.stat(file_1).st_mode
    f2_mode = os.stat(file_2).st_mode
    assert f1_mode == f2_mode, f"diff mode {file_1}({f1_mode:o}) {file_2}({f2_mode:o})"


@pytest.fixture(name="ctx")
def fixture_ctx(tmpdir: str) -> Context:
    """Create context fixture for running tests."""
    return Context(tmpdir)


def test_version_option() -> None:
    """Test --version option"""
    status = run_pylint_silent("--version")
    assert status == 0


def test_no_params() -> None:
    """Test exit error with no parameters."""
    status = run_pylint_silent()
    assert status == 2


def test_bad_params() -> None:
    """Test exit error with bad parameters."""
    status = run_pylint_silent("bad-param")
    assert status == 2


def test_apply(ctx: Context) -> None:
    """Test 'pylint-silent apply'."""
    # Run pylint on test files.
    pylint_output = ctx.temp_sample_filename + "lint"
    ctx.run_pylint_to_file(pylint_output)

    # Apply pylint-silent changed based on output from pylint.
    run_pylint_silent("apply", "--max-line-length=70", pylint_output)

    # Test that the expected python file was generated.
    assert_files_equal(ctx.temp_sample_filename, ctx.sample_after_apply)

    # Test that pylint is indeed silent now.
    exitcode = ctx.run_pylint("--disable=duplicate-code")
    assert exitcode == 0


def test_apply_signature(ctx: Context) -> None:
    """Test 'pylint-silent apply'."""
    # Run pylint on test files.
    pylint_output = ctx.temp_sample_filename + "lint"
    ctx.run_pylint_to_file(pylint_output)

    # Apply pylint-silent changed based on output from pylint.
    run_pylint_silent("apply", "--signature", pylint_output)

    # Test that the expected python file was generated.
    assert_files_equal(ctx.temp_sample_filename, ctx.sample_after_apply_w_sig)

    # Test that pylint is indeed silent now.
    exitcode = ctx.run_pylint("--disable=duplicate-code")
    assert exitcode == 0


def test_stats(ctx: Context) -> None:
    """Test that 'pylint-silent stats' have not changed."""
    sample_stats_1 = ctx.temp_sample_filename + "_stats_1"
    with redirect_stdout(open(sample_stats_1, "w", encoding="utf-8")):
        run_pylint_silent("stats", ctx.sample_after_apply)

    assert filecmp.cmp(sample_stats_1, ctx.sample_filename + "_stats"), \
        f"diff {sample_stats_1} {ctx.sample_filename + '_stats'}"

    # Test same result when running with --signature on a "legacy" apply
    sample_stats_2 = ctx.temp_sample_filename + "_stats_2"
    with redirect_stdout(open(sample_stats_2, "w", encoding="utf-8")):
        run_pylint_silent("stats", "--signature", ctx.sample_after_apply_w_sig)

    assert filecmp.cmp(sample_stats_2, ctx.sample_filename + "_stats"), \
        f"diff {sample_stats_2} {ctx.sample_filename + '_stats'}"

    # Test result when running with --signature on stats and apply
    sample_stats_3 = ctx.temp_sample_filename + "_stats_3"
    with redirect_stdout(open(sample_stats_3, "w", encoding="utf-8")):
        run_pylint_silent("stats", "--signature", ctx.sample_after_apply_mixed)

    assert filecmp.cmp(sample_stats_3, ctx.sample_filename + "_mixed_stats"), \
        f"diff {sample_stats_3} {ctx.sample_filename + '_mixed_stats'}"

    sample_stats_4 = ctx.temp_sample2_filename + "_stats_4"
    with redirect_stdout(open(sample_stats_4, "w", encoding="utf-8")):
        run_pylint_silent("stats", ctx.sample2_filename)

    assert filecmp.cmp(sample_stats_4, ctx.sample2_filename + "_stats"), \
        f"diff {sample_stats_4} {ctx.sample2_filename + '_stats'}"


def test_reset(ctx: Context) -> None:
    """Test 'pylint-silent reset'.
    Remove all generated comments and test that we are back to the original code.
    """
    run_pylint_silent("reset", ctx.temp_sample_after_apply)

    assert_files_equal(ctx.temp_sample_after_apply, ctx.sample_filename)

    # Test resetting a clean file.
    run_pylint_silent("reset", ctx.temp_sample_after_apply)

    assert_files_equal(ctx.temp_sample_after_apply, ctx.sample_filename)

    # Test resetting a file with signature.
    run_pylint_silent("reset", "--signature", ctx.temp_sample_after_apply_w_sig)

    assert_files_equal(ctx.temp_sample_after_apply_w_sig, ctx.sample_filename)


def test_reset_sample2(ctx: Context) -> None:
    """Test 'pylint-silent reset' of the second sample file.

    Remove all pylint comments and test that we preserve other comments
    """
    run_pylint_silent("reset", ctx.temp_sample2_filename)

    assert_files_equal(ctx.sample2_after_reset, ctx.temp_sample2_filename)

    # Test resetting a file without signatures but with --signature (should fail)
    run_pylint_silent("reset", "--signature", ctx.temp_sample2_again_filename)
    assert (
        filecmp.cmp(ctx.sample2_after_reset, ctx.temp_sample2_again_filename) is False
    )
