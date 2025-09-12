#!/usr/bin/env python3
import hypercorn
from hypercorn.config import Config
from app.main import app
from app.config import settings

if _name_ == "_main_":
    config = Config()
    config.bind = ["0.0.0.0:4000"]
    config.use_reload = settings.debug
    config.loglevel = "info"
    
    hypercorn.run(app, config)
