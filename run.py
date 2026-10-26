"""Start the NeuroFocus AI web app:  python run.py   then open http://127.0.0.1:5000"""

import os

from backend.app import create_app

app = create_app()

if __name__ == "__main__":
    # Debug mode is off by default; never enable it on a network-reachable host.
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5000)),
            debug=os.environ.get("NEUROFOCUS_DEBUG") == "1")
