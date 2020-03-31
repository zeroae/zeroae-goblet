from jinja2 import Environment, PackageLoader

j2: Environment = Environment(loader=PackageLoader(__name__, "templates"))


def render_setup_html(app_manifest, create_app_url):
    setup_html = j2.get_template("setup.jinja2")
    body = setup_html.render(create_app_url=create_app_url, manifest=app_manifest)
    return body
