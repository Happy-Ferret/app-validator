from js_helper import TestCase


class TestOverwrite(TestCase):
    """Test that JS variables can be properly overwritten."""

    def test_new_overwrite(self):
        """Tests that objects created with `new` can be overwritten."""

        self.run_script("""
        var x = new String();
        x += "asdf";
        x = "foo";
        """)
        self.assert_silent()

    def test_redefine_new_instance(self):
        """Test the redefinition of an instance of a global type."""

        self.run_script("""
        var foo = "asdf";
        var r = new RegEx(foo, "i");
        r = new RegExp(foo, "i");
        r = null;
        """)
        self.assert_silent()

    def test_property_members(self):
        """Tests that properties and members are treated fairly."""

        self.run_script("""
        var x = {"foo":"bar"};
        var y = x.foo;
        var z = x["foo"];
        """)
        self.assert_var_eq("y", "bar")
        self.assert_var_eq("z", "bar")

    def test_global_overwrite(self):
        """
        Make sure that we aren't testing for things that normally get
        overwritten in the other validator.
        """

        def test(self, script):
            self.setUp()
            self.run_script(script)
            self.assert_silent()

        yield test, self, 'Number = "asdf"'
        yield test, self, 'Number.prototype = "foo"'
        yield test, self, 'Number.prototype.test = "foo"'
        yield test, self, 'Number.prototype["test"] = "foo"'
        yield test, self, 'x = Number.prototype; x.test = "foo"'

    def test_with_statement_pass(self):
        """Tests that 'with' statements work as intended."""

        self.run_script("""
        var x = {"foo":"bar"};
        with(x) {
            foo = "zap";
        }
        var z = x["foo"];
        """)
        self.assert_silent()
        self.assert_var_eq("z", "zap")

    def test_with_statement_tested(self):
        """
        Assert that the contets of a with statement are still evaluated even if
        the context object is not available.
        """

        self.run_script("""
        with(foo.bar) { // These do not exist yet
            eval("evil");
        }
        """)
        self.assert_failed()

    def test_local_global_overwrite(self):
        """Test that a global assigned to a local variable can be overwritten."""

        self.run_script("""
        foo = String.prototype;
        foo = "bar";
        """)
        self.assert_silent()

    def test_overwrite_global(self):
        """Test that an overwritable global is overwritable."""

        self.run_script("""
        document.title = "This is something that isn't a global";
        """)
        self.assert_silent()

    def test_overwrite_readonly_false(self):
        """Test that globals with readonly set to false are overwritable."""

        self.run_script("""window.innerHeight = 123;""")
        self.assert_silent()
