import json

from chalice import Chalice
from environs import Env

from zeroae.goblet import chalice as goblet

# Load Configuration Options
env: Env = Env()
env.read_env()
goblet.configure(env)

# Register the Application
app = Chalice(app_name="chalice")
app.experimental_feature_flags.update(["BLUEPRINTS"])
app.register_blueprint(goblet.bp, name_prefix="gh")


@goblet.bp.on_gh_event("ping")
def ping(payload):
    app.log.info(json.dumps(payload))
