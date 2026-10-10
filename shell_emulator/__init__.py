"""UNIX-like virtual shell emulator."""
from .emulator import Emulator
from .vfs import VirtualFS, VFSError

__all__ = ["Emulator", "VirtualFS", "VFSError"]
