import os
import secrets
import shutil
import subprocess
import time
from pathlib import Path
import zmq


class OMCConnection:
    
    def __init__(self, random_socket_name=False, port=10000, start_timeout_s=20):
        self._port = int(port)
        self._omc_process = self._start_omc_process(random_socket_name)
        self._context = zmq.Context()
        self._omc_socket = self._create_client_socket()
        # quick readiness check
        self._wait_until_ready(timeout_s=start_timeout_s)

    def __del__(self):
        try:
            if getattr(self, "_omc_process", None):
                self._omc_process.terminate()
        except Exception:
            pass

    # ---- helpers, determines OMC path (windows or linux) ----
    def _find_omc(self):
        # 0) static override
        STATIC_OMC_EXE = r"C:\Program Files\OpenModelica1.22.1-64bit\bin\omc.exe"
        if STATIC_OMC_EXE and Path(STATIC_OMC_EXE).exists():
            return STATIC_OMC_EXE

        # 1) environment variable
        omc = os.environ.get("OMC_EXE")
        if omc and Path(omc).exists():
            return omc

        # 2) on PATH
        omc = shutil.which("omc.exe") or shutil.which("omc")
        if omc:
            return omc

        # 3) OPENMODELICAHOME (Windows installer usually sets this)
        omhome = os.environ.get("OPENMODELICAHOME")
        if omhome:
            cand = Path(omhome) / "bin" / "omc.exe"
            if cand.exists():
                return str(cand)

        raise FileNotFoundError(
            "Could not find omc. Set OMC_EXE, add it to PATH, or set OPENMODELICAHOME."
        )

    def _start_omc_process(self, random_socket_name):
        omc_executable = self._find_omc()
        cmd = [omc_executable, "--interactive=zmq", f"--interactivePort={self._port}"]
        if random_socket_name:
            # clean ASCII token, e.g. 'd9e3a2fbc1c84e33'
            cmd.append(f"-z={secrets.token_hex(8)}")

        # On Windows, avoid popping a console window (optional)
        creationflags = 0x08000000 if os.name == "nt" else 0  # CREATE_NO_WINDOW
        return subprocess.Popen(cmd, creationflags=creationflags)

    def _create_client_socket(self):
        sock = self._context.socket(zmq.REQ)
        sock.setsockopt(zmq.LINGER, 0)
        sock.connect(f"tcp://127.0.0.1:{self._port}")
        return sock

    def _wait_until_ready(self, timeout_s=20):
        deadline = time.time() + timeout_s
        while time.time() < deadline:
            try:
                self._omc_socket.send_string("getVersion()")
                if self._omc_socket.poll(1000) & zmq.POLLIN:
                    _ = self._omc_socket.recv_string()
                    return
            except Exception:
                pass
            time.sleep(0.1)
        raise TimeoutError("OMC did not become ready in time.")

    def request(self, expression, timeout=300000):
        self._omc_socket.send_string(expression)
        if self._omc_socket.poll(timeout) & zmq.POLLIN:
            return self._omc_socket.recv_string()
        raise TimeoutError(f"OMC request timed out: {expression}")
