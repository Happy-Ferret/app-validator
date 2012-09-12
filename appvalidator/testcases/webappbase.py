import base64
from cStringIO import StringIO

from PIL import Image
import requests

from . import register_test
from .. import constants
from ..webapp import detect_webapp_string


@register_test(tier=1)
def test_app_manifest(err, package):

    if "manifest.webapp" not in package:
        return err.error(
            err_id=("webappbase", "test_app_manifest", "missing_manifest"),
            error="Packaged app missing manifest",
            description=["All apps must contain an app manifest file.",
                         "Attempted to find a manifest at `/manifest.webapp`, "
                         "but no file was found."])

    webapp = detect_webapp_string(err, package.read("manifest.webapp"))
    err.save_resource("manifest", webapp)


class DataURIException(Exception):
    pass


def try_get_data_uri(data_url):
    # Strip off the leading "data:"
    data_url = data_url[5:]

    if ";" in data_url:
        data_url = data_url[data_url.find(";") + 1:]
    if "," in data_url:
        data_url = data_url[data_url.find(",") + 1:]

    try:
        decoded = base64.urlsafe_b64decode(data_url)
    except (TypeError, ValueError):
        raise DataURIException("Could not decode `data:` URI.")
    else:
        return decoded


def try_get_resource(err, package, url, filename, resource_type="URL",
                     max_size=True):
    # Try to process data URIs first.
    if url.startswith("data:"):
        try:
            return try_get_data_uri(url)
        except DataURIException as e:
            err.error(
                err_id=("resources", "data_uri_error"),
                error=str(e),
                description="A `data:` URI referencing a %s could not be "
                            "opened." % resource_type,
                filename=filename)
        return

    # Pull in whatever packaged app resources are required.
    if err.get_resource("packaged") and "://" not in url:
        url = url.lstrip("/")
        try:
            return package.read(url)
        except Exception:
            err.error(
                err_id=("resources", "packaged", "not_found"),
                error="Resource in packaged app not found.",
                description=["A resource within a packaged app is "
                             "referenced, but the path used does not "
                             "point to a valid item in the package.",
                             "Requested resource: %s" % url],
                filename=filename)
            return

    try:
        request = requests.get(url, prefetch=False)
        data = request.raw.read(constants.MAX_RESOURCE_SIZE)
        # Check that there's not more data than the max size.
        if max_size and request.raw.read(1):
            err.error(
                err_id=("resources", "too_large"),
                error="Resource too large",
                description=["A requested resource returned too much data. "
                             "File sizes are limited to %dMB." %
                                 (constants.MAX_RESOURCE_SIZE / 1204 / 1024),
                             "Requested resource: %s" % url],
                filename=filename)
            return

        request.raw.close()

        if not data:
            err.error(
                err_id=("resources", "null_response"),
                error="Null response when fetching %s" % resource_type,
                description=["A remote resource was requested, but no data "
                             "was returned.",
                             "Requested resource: %s" % url])

        return data

    except requests.exceptions.MissingSchema:
        err.error(
            err_id=("resources", "invalid_url", "schema"),
            error="Invalid URL",
            description=["While attempting to retrieve a remote resource, "
                         "an invalid URL was encountered. All URLs must "
                         "contain a schema.",
                         "URL: %s" % url],
            filename=filename)
    except requests.exceptions.URLRequired:
        err.error(
            err_id=("resources", "invalid_url", "none"),
            error="Invalid URL",
            description=["While attempting to retrieve a remote resource, "
                         "an invalid URL was encountered.",
                         "URL: %s" % url],
            filename=filename)
    except requests.exceptions.ConnectionError:
        err.error(
            err_id=("resources", "connection_error"),
            error="Connection Error when requesting %s" % resource_type,
            description=["While attempting to retrieve a remote resource, "
                         "a connection error was encountered. This may be "
                         "a DNS error, a connection refusal, or other low-"
                         "level socket exception.",
                         "Requested resource: %s" % url],
            filename=filename)
    except requests.exceptions.Timeout:
        err.warning(
            err_id=("resources", "timeout"),
            warning="Timeout when requesting %s" % resource_type,
            description=["While attempting to retrieve a remote resource, "
                         "a timeout was encountered. Try validating your "
                         "app again or contact your web host to see if there "
                         "is an issue with the hosting.",
                         "Requested resource: %s" % url],
            filename=filename)
    except requests.exceptions.HTTPError as e:
        err.error(
            err_id=("resources", "http_error"),
            error="'%s' when requesting %s" % (str(e), resource_type),
            description=["While attempting to retrieve a remote resource, "
                         "a timeout was encountered. Try validating your "
                         "app again or contact your web host to see if there "
                         "is an issue with the hosting.",
                         "Requested resource: %s" % url],
            filename=filename)
    except requests.exceptions.TooManyRedirects:
        err.error(
            err_id=("resources", "too_many_redirects"),
            error="Too many redirects for %s" % resource_type,
            description=["While attempting to retrieve a remote resource, "
                         "too many redirects were encountered. There should "
                         "never be more than a few redirects present at a "
                         "permanent URL in an app.",
                         "Requested resource: %s" % url],
            filename=filename)


def test_icon(err, data, url, size):
    try:
        icon = Image.open(data)
        icon.verify()
    except IOError:
        err.error(
            err_id=("resources", "icon", "ioerror"),
            error="Could not read icon file.",
            description=["A downloaded icon file could not be opened. It may "
                         "contain invalid or corrupt data. Icons may be only "
                         "JPG or PNG images.",
                         "%dpx icon (%s)" % (size, url)])
    else:
        width, height = icon.size
        if width != height:
            err.error(
                err_id=("resources", "icon", "square"),
                error="Icons must be square.",
                description=["A downloaded icon was found to have a different "
                             "width and height. All icons must be square.",
                             "%dpx icon (%s)" % (size, url),
                             "Dimensions: %d != %d" % (width, height)],
                filename="webapp.manifest")
        elif width != size:
            err.error(
                err_id=("resources", "icon", "size"),
                error="Icon size does not match.",
                description=["A downloaded icon was found to have a different "
                             "width and height than the size that it said it "
                             "was.",
                             "[Purported] %dpx icon (%s)" % (size, url),
                             "Found size: %dpx" % width],
                filename="webapp.manifest")


@register_test(tier=2)
def test_app_resources(err, package):

    # Do not test app resources if something else failed.
    if err.errors:
        return

    manifest = err.get_resource("manifest")
    if not manifest:
        return

    # Test the icons in the manifest. The manifest validator should have thrown
    # a hard error if this isn't a dict, so this won't ever be reached if it'll
    # otherwise fail with subscript errors.
    for icon_size, url in manifest.get("icons", {}).items():
        icon_data = try_get_resource(err, package,
                                     url, "webapp.manifest", "icon")
        if not icon_data:
            continue

        test_icon(err, data=StringIO(icon_data), url=url, size=icon_size)

    if "appcache_path" in manifest:
        try_get_resource(err, package, manifest["appcache_path"],
                         filename="webapp.manifest", resource_type="manifest",
                         max_size=False)

    def test_developer(branch):
        if branch and "url" in branch:
            try_get_resource(err, package, branch["url"],
                             filename="webapp.manifest",
                             resource_type="developer url", max_size=False)

    test_developer(manifest.get("developer"))
    for locale, locale_data in manifest.get("locales", {}).items():
        test_developer(locale_data.get("developer"))
