"""
Keep TAP to a single running instance.

The first instance listens on a named local socket. Later launches send it the
file they were asked to open (or an empty message, meaning "just come to the
front") and exit.
"""

import getpass
import sys

from PySide6.QtCore import QObject, Signal
from PySide6.QtNetwork import QLocalServer, QLocalSocket

_SERVER_NAME = f"TAP-MPS-{getpass.getuser()}"

def send_to_running_instance(path: str) -> bool:
    """Hand path to an already-running instance. Returns False if none is running."""
    sock = QLocalSocket()
    sock.connectToServer(_SERVER_NAME)
    if not sock.waitForConnected(500):
        return False

    if sys.platform == "win32":
        # Let the running instance bring itself to the foreground
        import ctypes
        ctypes.windll.user32.AllowSetForegroundWindow(-1)   # ASFW_ANY

    sock.write(path.encode("utf-8"))
    sock.waitForBytesWritten(1000)
    sock.disconnectFromServer()
    return True

class InstanceServer(QObject):
    # Emitted with the path another launch asked to open ("" = just activate)
    message_received = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._server = QLocalServer(self)
        QLocalServer.removeServer(_SERVER_NAME)   # clear a stale socket left by a crash (Unix)
        self._server.listen(_SERVER_NAME)
        self._server.newConnection.connect(self._on_new_connection)

    def _on_new_connection(self) -> None:
        sock = self._server.nextPendingConnection()
        buffer = bytearray()
        sock.readyRead.connect(lambda: buffer.extend(sock.readAll().data()))

        def on_disconnected():
            buffer.extend(sock.readAll().data())
            self.message_received.emit(buffer.decode("utf-8", errors="replace"))
            sock.deleteLater()
        sock.disconnected.connect(on_disconnected)

        # The sender may already have written and hung up before we got here
        if sock.state() == QLocalSocket.LocalSocketState.UnconnectedState:
            on_disconnected()
