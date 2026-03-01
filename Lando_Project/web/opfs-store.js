/**
 * OPFS persistence helpers for model weights + instinct tensors.
 * Browser support: Chromium-based browsers with File System Access + OPFS.
 */

export class OPFSStore {
  constructor(rootDirName = 'lando-iai') {
    this.rootDirName = rootDirName;
    this.root = null;
  }

  async init() {
    const opfsRoot = await navigator.storage.getDirectory();
    this.root = await opfsRoot.getDirectoryHandle(this.rootDirName, { create: true });
    return this.root;
  }

  async writeJSON(path, payload) {
    const handle = await this._fileHandle(path, true);
    const writable = await handle.createWritable();
    await writable.write(JSON.stringify(payload));
    await writable.close();
  }

  async readJSON(path, fallback = null) {
    try {
      const handle = await this._fileHandle(path, false);
      const file = await handle.getFile();
      return JSON.parse(await file.text());
    } catch {
      return fallback;
    }
  }

  async writeBlob(path, blob) {
    const handle = await this._fileHandle(path, true);
    const writable = await handle.createWritable();
    await writable.write(blob);
    await writable.close();
  }

  async exists(path) {
    try {
      await this._fileHandle(path, false);
      return true;
    } catch {
      return false;
    }
  }

  async _fileHandle(path, create) {
    if (!this.root) {
      await this.init();
    }
    const parts = path.split('/').filter(Boolean);
    const filename = parts.pop();
    let dir = this.root;

    for (const segment of parts) {
      dir = await dir.getDirectoryHandle(segment, { create });
    }
    return dir.getFileHandle(filename, { create });
  }
}
