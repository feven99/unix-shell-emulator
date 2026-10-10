"""Entirely in-memory virtual file system. XML is only read during startup."""
from __future__ import annotations

import base64
import binascii
import posixpath
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field


@dataclass
class Node:
    is_dir: bool
    content: bytes = b""
    children: dict[str, "Node"] = field(default_factory=dict)


class VFSError(Exception):
    pass


class VirtualFS:
    def __init__(self, xml_path: str):
        self.root = Node(True)
        tree = ET.parse(xml_path)
        root = tree.getroot()
        if root.tag != "vfs":
            raise VFSError("XML root element must be <vfs>")
        self._load(root, self.root)

    def _load(self, xml_parent: ET.Element, parent: Node):
        for item in xml_parent:
            if item.tag not in ("dir", "file"):
                raise VFSError(f"unsupported XML element: {item.tag}")
            name = item.get("name", "")
            if not name or name in (".", "..") or "/" in name or "\x00" in name:
                raise VFSError(f"invalid entry name: {name!r}")
            if name in parent.children:
                raise VFSError(f"duplicate entry name: {name}")
            if item.tag == "dir":
                node = Node(True)
                parent.children[name] = node
                self._load(item, node)
            else:
                if len(item):
                    raise VFSError(f"file cannot have children: {name}")
                if item.get("encoding", "base64") != "base64":
                    raise VFSError(f"file encoding must be base64: {name}")
                try:
                    data = base64.b64decode("".join((item.text or "").split()), validate=True)
                except (ValueError, binascii.Error) as exc:
                    raise VFSError(f"invalid base64 for {name}") from exc
                parent.children[name] = Node(False, content=data)

    @staticmethod
    def normalize(path: str, cwd: str = "/") -> str:
        if not path:
            path = "."
        return posixpath.normpath(path if path.startswith("/") else posixpath.join(cwd, path))

    def get(self, path: str, cwd: str = "/") -> Node:
        full = self.normalize(path, cwd)
        node = self.root
        if full == "/":
            return node
        for part in full.strip("/").split("/"):
            if not node.is_dir:
                raise VFSError(f"{full}: not a directory")
            if part not in node.children:
                raise VFSError(f"{full}: no such file or directory")
            node = node.children[part]
        return node

    def listdir(self, path: str, cwd: str = "/") -> list[str]:
        node = self.get(path, cwd)
        if not node.is_dir:
            raise VFSError(f"{self.normalize(path, cwd)}: not a directory")
        return sorted(node.children)

    def copy(self, source: str, destination: str, cwd: str = "/") -> str:
        src_path = self.normalize(source, cwd)
        src = self.get(src_path)
        if src.is_dir:
            raise VFSError(f"{source}: omitting directory (cp supports files only)")
        dst_path = self.normalize(destination, cwd)
        try:
            dst = self.get(dst_path)
        except VFSError:
            dst = None
        if dst is not None and dst.is_dir:
            dst_path = self.normalize(posixpath.join(dst_path, posixpath.basename(src_path)))
        if src_path == dst_path:
            raise VFSError("source and destination are the same file")
        parent_path, name = posixpath.split(dst_path)
        parent = self.get(parent_path or "/")
        if not parent.is_dir:
            raise VFSError(f"{parent_path}: not a directory")
        if dst is not None and not dst.is_dir and dst_path != self.normalize(destination, cwd):
            raise VFSError(f"{destination}: invalid destination")
        parent.children[name] = Node(False, content=src.content)
        return dst_path
