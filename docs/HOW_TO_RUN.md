# How to run NeuroFocus AI (VS Code, step by step)

## One-time setup

1. **Install Python 3.10 or newer** from <https://www.python.org/downloads/>.
   On Windows, tick **"Add Python to PATH"** on the first installer screen.
2. **Install VS Code** and its **Python** extension (VS Code suggests it when
   you open the project).
3. **Get the code.** In VS Code: press `Ctrl+Shift+P`, choose
   **Git: Clone**, paste `https://github.com/ishanveeramalli82/Neurofocus-AI.git`,
   pick a folder such as `Documents`, then click **Open** when asked.
   (If you don't have Git: on the GitHub page click **Code > Download ZIP**,
   unzip it, and open the unzipped folder with **File > Open Folder**.)
4. **Install the libraries.** Open **Terminal > New Terminal** and run:

   ```
   pip install -r requirements.txt
   ```

   If `pip` is not recognized, use `python -m pip install -r requirements.txt`
   (Mac: `python3 -m pip install -r requirements.txt`).

## Every time

* **Start the app:** press **F5** and choose **Run NeuroFocus AI (web app)**,
  or type `python run.py` in the terminal.
* Open **<http://127.0.0.1:5000>** in Chrome or Edge.
* Create an account, click **Focus Session**, and allow the camera.
* **Stop:** press `Ctrl+C` in the terminal (or the red square in VS Code).

The camera only works at `127.0.0.1` or `localhost` (a browser security rule).
The face-tracking model is included in the repository, so after installing the
libraries the app works without internet.

## Other commands

| What | Command | VS Code (F5 menu) |
|---|---|---|
| Run the tests | `python -m pytest` | Run tests |
| Run the official experiment | `python -m research.pipeline.run_experiment --config research/config/experiment_v1.json` | Run official experiment |
| Run the exploratory experiment | `python -m research.pipeline.run_experiment --config research/config/onset_sweep_v1.json` | |

Before the official experiment, complete the checklist in
[`research/docs/02_procedure.md`](../research/docs/02_procedure.md).

## Troubleshooting

| Problem | Fix |
|---|---|
| `python` is not recognized | Install Python with "Add Python to PATH" ticked, then restart VS Code. |
| `No module named flask` | VS Code is using a different Python. `Ctrl+Shift+P` > **Python: Select Interpreter**, pick the one you installed, run the `pip install` step again. |
| Camera does not start | Use `http://127.0.0.1:5000`, allow camera access in the browser, and close other apps using the camera (Zoom, Teams). |
| `Address already in use` | The app is already running in another terminal. Stop it with `Ctrl+C`. |
| "Calibration needs another try" | Sit facing the screen with your face well lit, and keep still during the centre phase. |
