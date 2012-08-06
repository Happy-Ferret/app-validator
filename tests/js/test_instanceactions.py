from js_helper import _do_test_raw, TestCase

def test_createElement():
    """Tests that createElement calls are filtered properly"""

    assert not _do_test_raw("""
    var x = "foo";
    x.createElement();
    x.createElement("foo");
    """).failed()

    assert _do_test_raw("""
    var x = "foo";
    x.createElement("script");
    """).failed()

    assert _do_test_raw("""
    var x = "foo";
    x.createElement(bar);
    """).failed()


def test_createElementNS():
    """Tests that createElementNS calls are filtered properly"""

    assert not _do_test_raw("""
    var x = "foo";
    x.createElementNS();
    x.createElementNS("foo");
    x.createElementNS("foo", "bar");
    """).failed()

    assert _do_test_raw("""
    var x = "foo";
    x.createElementNS("foo", "script");
    """).failed()

    assert _do_test_raw("""
    var x = "foo";
    x.createElementNS("foo", bar);
    """).failed()


def test_setAttribute():
    """Tests that setAttribute calls are blocked successfully"""

    assert not _do_test_raw("""
    var x = "foo";
    x.setAttribute();
    x.setAttribute("foo");
    x.setAttribute("foo", "bar");
    """).failed()

    assert _do_test_raw("""
    var x = "foo";
    x.setAttribute("onfoo", "bar");
    """).notices


def test_callexpression_argument_traversal():
    """
    This makes sure that unknown function calls still have their arguments
    traversed.
    """

    assert not _do_test_raw("""
    function foo(x){}
    foo({"bar":function(){
        bar();
    }});
    """).failed()

    assert _do_test_raw("""
    function foo(x){}
    foo({"bar":function(){
        eval("evil");
    }});
    """).failed()


def test_insertAdjacentHTML():
    """Test that insertAdjacentHTML works the same as innerHTML."""

    assert not _do_test_raw("""
    var x = foo();
    x.insertAdjacentHTML("foo bar", "<div></div>");
    """).failed()

    assert _do_test_raw("""
    var x = foo();
    x.insertAdjacentHTML("foo bar", "<div onclick=\\"foo\\"></div>");
    """).failed()

    # Test without declaration
    assert _do_test_raw("""
    x.insertAdjacentHTML("foo bar", "<div onclick=\\"foo\\"></div>");
    """).failed()

    assert _do_test_raw("""
    var x = foo();
    x.insertAdjacentHTML("foo bar", "x" + y);
    """).failed()
