#!/usr/bin/env python

import uvicorn

uvicorn.run(
        "gui:app",
        host="127.0.0.1",
        port=8000,
    )
