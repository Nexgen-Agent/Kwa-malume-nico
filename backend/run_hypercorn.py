
#!/usr/bin/env python3
import hypercorn
from app.main import app
from app.config import settings
from hypercorn.config import Config

if __name__ == "__main__":
    config = Config()
    config.bind = ["0.0.0.0:4000"]
    config.use_reloader = settings.debug

    hypercorn.run(app, config)