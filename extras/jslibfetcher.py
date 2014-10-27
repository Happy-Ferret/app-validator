import urllib
import os


def process(url, destination):
    destination = "jslibs/%s" % destination

    if os.path.exists(destination):
        return

    try:
        print url
        urllib.urlretrieve(url, destination)
    except Exception as e:
        print "Failed", e


def get_pattern(prefix, url_pattern, versions):
    for version in versions:
        url = url_pattern % version
        process(url, "%s.%s.%s" % (prefix, version, url.split("/")[-1]))


BACKBONE_VERSIONS = [
    "1.0.0",
    "1.1.0",
    "1.1.1",
    "1.1.2",
]
DOJO_VERSIONS = [
    "1.4.0",
    "1.4.1",
    "1.4.3",
    "1.5",
    "1.5.1",
    "1.6",
    "1.6.1",
    "1.7.0",
    "1.7.1",
    "1.7.2",
    "1.7.3",
    "1.8.0",
    "1.8.1",
    "1.8.2",
    "1.8.3",
    "1.8.4",
    "1.8.5",
    "1.8.6",
    "1.9.0",
    "1.9.1",
    "1.9.2",
    "1.9.3",
]
# Google doesn't yet host EXT4.*
EXT_VERSIONS = [
    "3.0.0",
    "3.1.0",
]
JQUERY_VERSIONS = [
    "1.0.1",
    "1.0.2",
    "1.0.3",
    "1.0.4",
    "1.1",
    "1.1.1",
    "1.1.2",
    "1.4",
    "1.4.1",
    "1.4.2",
    "1.4.4",
    "1.5",
    "1.5.1",
    "1.5.2",
    "1.6",
    "1.6.1",
    "1.6.2",
    "1.6.3",
    "1.6.4",
    "1.7",
    "1.7.1",
    "1.7.2",
    "1.8.0",
    "1.8.1",
    "1.8.2",
    "1.8.3",
    "1.9.0",
    "1.9.1",
    "2.0.0",
    "2.0.1",
    "2.0.2",
    "2.0.3",
    "1.10.0",
    "1.10.1",
    "1.10.2",
    "2.0.0",
    "2.0.1",
    "2.0.2",
    "2.0.3",
    "1.11.0",
    "2.1.0",
    "1.11.1",
    "2.1.1",
]
JQUERYUI_VERSIONS = [
    "1.5.2",
    "1.5.3",
    "1.6.0",
    "1.7.0",
    "1.7.1",
    "1.7.2",
    "1.7.3",
    "1.8.0",
    "1.8.1",
    "1.8.2",
    "1.8.4",
    "1.8.5",
    "1.8.6",
    "1.8.7",
    "1.8.8",
    "1.8.9",
    "1.8.10",
    "1.8.11",
    "1.8.12",
    "1.8.13",
    "1.8.14",
    "1.8.15",
    "1.8.16",
    "1.8.17",
    "1.8.18",
    "1.8.19",
    "1.8.20",
    "1.8.21",
    "1.8.22",
    "1.8.23",
    "1.8.24",
    "1.9.0",
    "1.9.1",
    "1.9.2",
    "1.10.0",
    "1.10.1",
    "1.10.2",
    "1.10.3",
    "1.10.4",
    "1.11.0",
    "1.11.1",
]
MOOTOOLS_VERSIONS = [
    "1.1.1",
    "1.1.2",
    "1.2.1",
    "1.2.2",
    "1.2.3",
    "1.2.4",
    "1.2.5",
    "1.3.0",
    "1.3.1",
    "1.3.2",
    "1.4.0",
    "1.4.1",
    "1.4.2",
    "1.4.3",
    "1.4.4",
    "1.4.5",
    "1.5.0",
]
PROTOTYPE_VERSIONS = [
    "1.6.0.2",
    "1.6.0.3",
    "1.6.1.0",
    "1.7.0.0",
    "1.7.1.0",
    "1.7.2.0",
]
REQUIREJS_VERSIONS = [
    '2.0.0',
    '2.0.2',
    '2.0.3',
    '2.0.4',
    '2.0.5',
    '2.0.6',
    '2.1.0',
    '2.1.1',
    '2.1.2',
    '2.1.3',
    '2.1.4',
    '2.1.5',
    '2.1.6',
    '2.1.7',
    '2.1.8',
    '2.1.9',
    '2.1.10',
    '2.1.11',
    '2.1.12',
    '2.1.13',
    '2.1.14',
    '2.1.15',
]
REQUIREJS_DOMREADY_VERSIONS = [
    "2.0.0",
    "2.0.1"
]
REQUIREJS_I18N_VERSIONS = [
    "2.0.0",
    "2.0.1",
    "2.0.2",
    "2.0.3",
    "2.0.4",
]
REQUIREJS_TEXT_VERSIONS = [
    '2.0.0',
    '2.0.2',
    '2.0.3',
    '2.0.4',
    '2.0.5',
    '2.0.6',
    '2.0.9',
    '2.0.10',
    '2.0.11',
    '2.0.12',
]
SCRIPTACULOUS_VERSIONS = [
    "1.8.1",
    "1.8.2",
    "1.8.3",
    "1.9.0",
]
SWFOBJECT_VERSIONS = [
    "2.1", "2.2",
]
UNDERSCORE_VERSIONS = [
    "1.6.0",
    "1.5.2",
    "1.5.1",
    "1.5.0",
    "1.4.4",
    "1.4.3",
    "1.4.2",
    "1.4.1",
    "1.4.0",
    "1.3.3",
    "1.3.2",
    "1.3.1",
    "1.3.0",
    "1.2.4",
    "1.2.3",
    "1.2.2",
    "1.2.1",
    "1.2.0",
    "1.1.7",
    "1.1.6",
    "1.1.5",
    "1.1.4",
    "1.1.3",
    "1.1.2",
    "1.1.1",
    "1.1.0",
    "1.0.4",
    "1.0.3",
    "1.0.2",
    "1.0.1",
    "1.0.0",
]
YUI_VERSIONS = [
    "2.6.0",
    "2.7.0",
    "2.8.0r4",
    "2.8.1",
    "2.8.2",
    "2.9.0",
]
YUI_NEW_VERSIONS = [
    "3.3.0",
    "3.4.0",
    "3.4.1",
    "3.5.0",
    "3.5.1",
    "3.6.0",
]


# Backbone
get_pattern("backbone",
        "https://raw.githubusercontent.com/jashkenas/backbone/%s/backbone.js",
        BACKBONE_VERSIONS)
get_pattern("backbone",
        "https://raw.githubusercontent.com/jashkenas/backbone/%s/backbone-min.js",
        BACKBONE_VERSIONS)

# Dojo Toolkit
get_pattern(
    "dojo",
    "http://download.dojotoolkit.org/release-%s/dojo.js",
    DOJO_VERSIONS)
get_pattern(
    "dojo",
    "http://download.dojotoolkit.org/release-%s/dojo.js.uncompressed.js",
    DOJO_VERSIONS)

# EXT.js
get_pattern(
    "ext-core",
    "https://ajax.googleapis.com/ajax/libs/ext-core/%s/ext-core.js",
    EXT_VERSIONS)
get_pattern(
    "ext-debug",
    "https://ajax.googleapis.com/ajax/libs/ext-core/%s/ext-core-debug.js",
    EXT_VERSIONS)

# jQuery
get_pattern(
    "jquery",
    "http://code.jquery.com/jquery-%s.js",
    JQUERY_VERSIONS)
get_pattern(
    "jquery",
    "http://code.jquery.com/jquery-%s.min.js",
    JQUERY_VERSIONS)

# jQueryUI
get_pattern(
    "jqueryui",
    "https://ajax.googleapis.com/ajax/libs/jqueryui/%s/jquery-ui.min.js",
    JQUERYUI_VERSIONS)
get_pattern("jqueryui",
    "https://ajax.googleapis.com/ajax/libs/jqueryui/%s/jquery-ui.js",
    JQUERYUI_VERSIONS)

# MooTools
get_pattern(
    "mootools",
    "https://ajax.googleapis.com/ajax/libs/mootools/%s/mootools-yui-compressed.js",
    MOOTOOLS_VERSIONS)
get_pattern(
    "mootools",
    "https://ajax.googleapis.com/ajax/libs/mootools/%s/mootools.js",
    MOOTOOLS_VERSIONS)

# Prototype.js
get_pattern(
    "prototype",
    "https://ajax.googleapis.com/ajax/libs/prototype/%s/prototype.js",
    PROTOTYPE_VERSIONS)

# Require.js
get_pattern(
    "requirejs",
    "http://requirejs.org/docs/release/%s/minified/require.js",
    REQUIREJS_VERSIONS)
get_pattern(
    "requirejs-commented",
    "http://requirejs.org/docs/release/%s/comments/require.js",
    REQUIREJS_VERSIONS)

get_pattern(
    "requirejs-domReady",
    "https://raw.githubusercontent.com/requirejs/domReady/%s/domReady.js",
    REQUIREJS_DOMREADY_VERSIONS)

get_pattern(
    "requirejs-i18n",
    "https://raw.githubusercontent.com/requirejs/i18n/%s/i18n.js",
    REQUIREJS_I18N_VERSIONS)

get_pattern(
    "requirejs-text",
    "https://raw.githubusercontent.com/requirejs/text/%s/text.js",
    REQUIREJS_TEXT_VERSIONS)

# Scriptaculous
get_pattern(
    "scriptaculous",
    "https://ajax.googleapis.com/ajax/libs/scriptaculous/%s/scriptaculous.js",
    SCRIPTACULOUS_VERSIONS)

# SWFObject
get_pattern(
    "swfobject",
    "https://ajax.googleapis.com/ajax/libs/swfobject/%s/swfobject.js",
    SWFOBJECT_VERSIONS)
get_pattern(
    "swfobject",
    "https://ajax.googleapis.com/ajax/libs/swfobject/%s/swfobject_src.js",
    SWFOBJECT_VERSIONS)

# Underscore
get_pattern(
    "underscore",
    "https://raw.github.com/documentcloud/underscore/%s/underscore.js",
    UNDERSCORE_VERSIONS)
get_pattern(
    "underscore",
    "https://raw.github.com/documentcloud/underscore/%s/underscore-min.js",
    UNDERSCORE_VERSIONS)

# Old-style YUI loader libraries:
get_pattern(
    "yui",
    "http://yui.yahooapis.com/%s/build/yuiloader/yuiloader-min.js",
    YUI_VERSIONS)
get_pattern(
    "yui",
    "http://yui.yahooapis.com/%s/build/yuiloader/yuiloader.js",
    YUI_VERSIONS)

# New-style YUI libraries
get_pattern(
    "yui",
    "http://yui.yahooapis.com/%s/build/yui-base/yui-base-min.js",
    YUI_NEW_VERSIONS)
get_pattern(
    "yui",
    "http://yui.yahooapis.com/%s/build/yui-base/yui-base.js",
    YUI_NEW_VERSIONS)


CRYPTO_FILES = ["aes", "cipher-core", "core", "enc-base64", "enc-utf16",
                "evpkdf", "hmac", "md5", "mode-cfb", "mode-ctr", "mode-ecb",
                "mode-ofb", "pad-ansix923", "pad-iso10126", "pad-iso97971",
                "pad-nopadding", "pad-zeropadding", "pbkdf2", "rabbit", "rc4",
                "sha1", "sha224", "sha256", "sha384", "sha512", "tripledes",
                "x64-core"]
get_pattern(
    "crypto_js",
    "http://crypto-js.googlecode.com/svn/tags/3.0.2/src/%s.js",
    CRYPTO_FILES)


get_pattern(
    "webl10n",
    "https://raw.githubusercontent.com/fabi1cazenave/webL10n/%s/l10n.js",
    ['master'])
