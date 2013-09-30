import instanceproperties


class JSObject(object):
    """
    Mimics a JS object (function) and is capable of serving as an active
    context to enable static analysis of `with` statements.
    """

    def __init__(self, data=None):
        self.type_ = "object"  # For use when an object is pushed as a context.
        self.data = {u"prototype": lambda: JSPrototype()}
        if data:
            self.data.update(data)

        self.recursing = False

    def get(self, name, instantiate=False, traverser=None):
        "Returns the value associated with a property name"
        name = unicode(name)
        output = None

        if name in self.data:
            output = self.data[name]
            if callable(output):
                output = output()
        elif instantiate:
            output = JSWrapper(JSObject(), dirty=True, traverser=traverser)
            self.set(name, output, traverser=traverser)

        if traverser:
            modifier = instanceproperties.get_operation("get", name)
            if modifier:
                modifier(traverser)

        dirty = False
        if output is None:
            dirty = True
            output = JSObject()

        if dirty or not isinstance(output, JSWrapper):
            output = JSWrapper(output, dirty=dirty, traverser=traverser)
        return output

    def get_literal_value(self):
        return u"[object Object]"

    def set(self, name, value, traverser=None):
        if traverser:
            modifier = instanceproperties.get_operation("set", name)
            if modifier:
                modified_value = modifier(value, traverser)
                if modified_value is not None:
                    value = modified_value

        self.data[name] = value

    def has_var(self, name):
        return unicode(name) in self.data

    def output(self):
        if self.recursing:
            return u"(recursion)"

        # Prevent unruly recursion with a recursion buster.
        self.recursing = True

        output_dict = {}
        for key in self.data.keys():
            if callable(self.data[key]):
                continue
            elif (isinstance(self.data[key], JSWrapper) and
                  self.data[key].value == self):
                output_dict[key] = u"(self)"
            elif self.data[key] is None:
                output_dict[key] = u"(None)"
            else:
                output_dict[key] = self.data[key].output()

        # Pop from the recursion buster.
        self.recursing = False

        return str(output_dict)


class JSContext(JSObject):
    """A variable context"""

    def __init__(self, context_type):
        super(JSContext, self).__init__()
        self.type_ = context_type
        self.data = {}


class JSWrapper(object):
    """Wraps a JS value and handles contextual functions for it."""

    def __init__(self, value=None, dirty=False, lazy=False,
                 is_global=False, traverser=None, callable_=False,
                 setter=None, context="chrome"):

        if is_global:
            assert not value

        if traverser is not None:
            traverser.debug_level += 1
            traverser._debug("-----New JSWrapper-----")
            if isinstance(value, JSWrapper):
                traverser._debug(">>> Rewrap <<<")
            traverser.debug_level -= 1

        self.const = False
        self.traverser = traverser
        self.value = None  # Instantiate the placeholder value
        self.is_global = False  # Not yet...
        self.dirty = False  # Also not yet...
        self.context = context

        # Used for predetermining set operations
        self.setter = setter

        if value is not None:
            self.set_value(value, overwrite_const=True)

        if not self.is_global:
            self.is_global = is_global  # Globals are built seperately

        self.dirty = dirty or self.dirty
        self.lazy = lazy
        self.callable = callable_

    def set_value(self, value, traverser=None, overwrite_const=False):
        """Assigns a value to the wrapper"""

        # Use a global traverser if it's present.
        if traverser is None:
            traverser = self.traverser

        if self.const and not overwrite_const:
            traverser.err.warning(
                err_id=("testcases_javascript_traverser", "JSWrapper_set_value",
                        "const_overwrite"),
                warning="Overwritten constant value",
                description="A variable declared as constant has been "
                            "overwritten in some JS code.",
                filename=traverser.filename,
                line=traverser.line,
                column=traverser.position,
                context=traverser.context)

        # Process any setter/modifier
        if self.setter:
            traverser._debug("Running setter on JSWrapper...");
            value = self.setter(value, traverser) or value or None

        if value == self.value:
            return self

        if isinstance(value, (bool, str, int, float, long, unicode)):
            self.inspect_literal(value)
            value = JSLiteral(value)
        # If the value being assigned is a wrapper as well, copy it in
        elif isinstance(value, JSWrapper):
            self.value = value.value
            self.lazy = value.lazy
            self.dirty = value.dirty
            self.is_global = value.is_global
            self.context = value.context
            # const does not carry over on reassignment
            return self
        elif callable(value):
            value = value(t=traverser)

        if not isinstance(value, dict):
            self.is_global = False
        elif "context" in value:
            self.context = value["context"]

        self.value = value
        return self

    def has_property(self, prop):
        """Returns a boolean value representing the presence of a property"""
        return (getattr(self.value, "has_var") and
                self.value.has_var(prop))

    def get(self, traverser, name, instantiate=False):
        """Retrieve a property from the variable."""

        value = self.value
        dirty = value is None
        context = self.context
        if self.is_global:
            if "value" not in value:
                output = JSWrapper(JSObject(), traverser=traverser)
                output.value = {}

                def apply_value(name):
                    if name in self.value:
                        output.value[name] = self.value[name]

                map(apply_value, ("dangerous", "readonly", "context", "name"))
                output.is_global = True
                output.context = self.context
                return output

            def _evaluate_lambdas(node):
                if callable(node):
                    return _evaluate_lambdas(node(t=traverser))
                else:
                    return node

            value_val = value["value"]
            value_val = _evaluate_lambdas(value_val)

            if isinstance(value_val, dict):
                if name in value_val:
                    value_val = _evaluate_lambdas(value_val[name])
                    output = traverser._build_global(name=name,
                                                     entity=value_val)
                    if "context" not in value_val:
                        output.context = self.context
                    return output
            else:
                value = value_val

        # Process any getters that are present for the current property.
        modifier = instanceproperties.get_operation("get", name)
        if modifier:
            modifier(traverser)

        if value is not None and issubclass(type(value), JSObject):
            output = value.get(name, instantiate=instantiate,
                               traverser=traverser)
        else:
            output = None

        if not isinstance(output, JSWrapper):
            output = JSWrapper(
                output, traverser=traverser, dirty=output is None or dirty)

        output.context = context

        # If we can predetermine the setter for the wrapper, we can save a ton
        # of lookbehinds in the future. This greatly simplifies the
        # MemberExpression support.
        setter = instanceproperties.get_operation("set", name)
        if setter:
            output.setter = setter
        return output

    def del_value(self, member):
        """The member `member` will be deleted from the value of the wrapper"""
        if self.is_global:
            self.traverser.err.warning(
                err_id=("testcases_js_jstypes", "del_value",
                        "global_member_deletion"),
                warning="Global member deletion",
                description="Members of global objects cannot be deleted.",
                filename=self.traverser.filename,
                line=self.traverser.line,
                column=self.traverser.position,
                context=self.traverser.context)
        elif isinstance(self.value, (JSObject, JSPrototype)):
            if member not in self.value.data:
                return
            del self.value.data[member]

    def contains(self, value):
        """Serves 'in' for BinaryOperators for lists and dictionaries"""

        # Unwrap the rvalue.
        if isinstance(value, JSWrapper):
            value = value.get_literal_value()

        if isinstance(self.value, JSArray):
            from actions import _get_as_num
            index = int(_get_as_num(value))
            if len(self.value.elements) > index >= 0:
                return True

        if isinstance(self.value, (JSArray, JSObject, JSPrototype)):
            return self.value.has_var(value)

        # Nothing else supports "in"
        return False

    def is_literal(self):
        """Returns whether the content is a literal"""
        return isinstance(self.value, JSLiteral)

    def get_literal_value(self):
        """Returns the literal value of the wrapper"""

        if self.is_global:
            if "literal" in self.value:
                return self.value["literal"](self.traverser)
            else:
                return "[object Object]"
        if self.value is None:
            return None

        output = self.value.get_literal_value()
        return output

    def output(self):
        """Returns a readable version of the object"""
        if self.value is None:
            return "(None)"
        elif self.is_global:
            return "(Global)"

        return self.value.output()

    def inspect_literal(self, value):
        """
        Inspect the value of a literal to see whether it contains a flagged
        value.
        """
        return  # This is currently a noop.

        # Don't do any processing if we can't return an error.
        if not self.traverser:
            return

        self.traverser._debug("INSPECTING: %s" % value)

        # This is a no-op for now.
        pass

    def __str__(self):
        """Returns a textual version of the object."""
        return unicode(self.get_literal_value())


class JSLiteral(JSObject):
    """Represents a literal JavaScript value."""

    def __init__(self, value=None):
        super(JSLiteral, self).__init__()
        self.value = value

    def set_value(self, value):
        self.value = value

    def __str__(self):
        if isinstance(self.value, bool):
            return str(self.output()).lower()
        return str(self.output())

    def output(self):
        return self.value

    def get_literal_value(self):
        "Returns the literal value of a this literal. Heh."
        return self.value


class JSPrototype(JSObject):
    """
    A lazy JavaScript object that is assumed not to contain any default
    methods.
    """

    def __init__(self):
        super(JSPrototype, self).__init__()
        self.data = {}

    def get(self, name, instantiate=False, traverser=None):
        name = unicode(name)
        output = super(JSPrototype, self).get(name, instantiate, traverser)
        if output is not None:
            return output
        if name == "prototype":
            prototype = JSWrapper(JSPrototype(), traverser=traverser)
            self.data[name] = prototype

        return output


class JSArray(JSObject):
    """A class that represents both a JS Array and a JS list."""

    def __init__(self):
        super(JSArray, self).__init__()
        self.elements = []

    def get(self, index, instantiate=False, traverser=None):
        if index == "length":
            return len(self.elements)

        # Courtesy of Ian Bicking: http://bit.ly/hxv6qt
        try:
            return self.elements[int(index.strip().split()[0])]
        except (ValueError, IndexError, KeyError):
            return super(JSArray, self).get(index, instantiate, traverser)

    def get_literal_value(self):
        """Arrays return a comma-delimited version of themselves."""

        if self.recursing:
            return u"(recursion)"

        self.recursing = True

        # Interestingly enough, this allows for things like:
        # x = [4]
        # y = x * 3 // y = 12 since x equals "4"

        output = u",".join(
            [unicode(w.get_literal_value() if w is not None else u"") for w in
             self.elements if
             not (isinstance(w, JSWrapper) and w.value == self)])

        self.recursing = False
        return output

    def set(self, index, value, traverser=None):
        try:
            index = int(index)
            f_index = float(index)
            # Ignore floating point indexes
            if index != float(index) or index < 0:
                return super(JSArray, self).set(value, traverser)
        except ValueError:
            return super(JSArray, self).set(index, value, traverser)

        if len(self.elements) > index:
            self.elements[index] = JSWrapper(value=value, traverser=traverser)
        else:
            # Max out the array size at 100000
            index = min(index, 100000)
            # Assigning to an index higher than the top of the list pads the
            # list with nulls
            while len(self.elements) < index:
                self.elements.append(None)
            self.elements.append(JSWrapper(value=value, traverser=traverser))

    def output(self):
        return u"[%s]" % self.get_literal_value()
