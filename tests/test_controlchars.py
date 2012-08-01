import sys

from nose.tools import eq_

from appvalidator.errorbundler import ErrorBundle
from appvalidator.outputhandlers.shellcolors import OutputHandler
import appvalidator.unicodehelper
import appvalidator.testcases.scripting


# Originated from bug 626496
def _do_test(path):
    script = appvalidator.unicodehelper.decode(open(path, "rb").read())
    print script.encode("ascii", "replace")

    err = ErrorBundle(instant=True)
    err.supported_versions = {}
    err.handler = OutputHandler(sys.stdout, False)
    appvalidator.testcases.scripting.test_js_file(err, path, script)
    return err


def test_controlchars_ascii_ok():
    """Test that multi-byte characters are decoded properly (utf-8)."""

    errs = _do_test("tests/resources/controlchars/controlchars_ascii_ok.js")
    assert not errs.message_count


def test_controlchars_ascii_warn():
    """
    Test that multi-byte characters are decoded properly (utf-8) but remaining
    non ascii characters raise warnings.
    """

    errs = _do_test("tests/resources/controlchars/controlchars_ascii_warn.js")
    eq_(errs.message_count, 1)
    eq_(errs.warnings[0]["id"][2], "syntax_error")


def test_controlchars_utf8_ok():
    """Test that multi-byte characters are decoded properly (utf-8)."""

    errs = _do_test("tests/resources/controlchars/controlchars_utf-8_ok.js")
    assert not errs.message_count


def test_controlchars_utf8_warn():
    """
    Tests that multi-byte characters are decoded properly (utf-8) but remaining
    non-ascii characters raise warnings.
    """

    errs = _do_test("tests/resources/controlchars/controlchars_utf-8_warn.js")
    eq_(errs.message_count, 1)
    eq_(errs.warnings[0]["id"][2], "syntax_error")

