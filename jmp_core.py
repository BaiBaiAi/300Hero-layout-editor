from __future__ import annotations

import glob
import hashlib
import json
import os
import struct
import time
import zlib
import threading
import tempfile
import re
from dataclasses import dataclass, field

MAGIC = (b'DATA1.0', b'DATA2.0')
HEXSET = set(b'0123456789abcdef')
STRIDE = 304
PATH_FIELD = 260
HDR = 54
_PACK_LOCKS = {}
_LOCK_GUARD = threading.Lock()


def standard_header(head):
    return bool(re.fullmatch(rb'DATA[0-9]+\.[0-9]+',head[:50].split(b'\0',1)[0]))


def pack_lock(path):
    key = os.path.normcase(os.path.abspath(path))
    with _LOCK_GUARD:
        return _PACK_LOCKS.setdefault(key, threading.RLock())


def refresh_entry(pk, e):
    """Refresh mutable offsets/sizes after a patch, restore or external update."""
    with pack_lock(pk.file), open(pk.file, 'rb') as f:
        head=f.read(HDR)
        if len(head)!=HDR or (not standard_header(head) and
                not (pk.parse_ok and pk.nonstandard_verified and head[:50]==pk.header)):
            raise JmpError('资源包头已改变，请重新加载资源包')
        count=struct.unpack_from('<I',head,50)[0]
        if not 0 <= e.index < count:
            raise JmpError('资源索引超出当前包范围')
        f.seek(e.rec)
        record = f.read(STRIDE)
        if len(record) != STRIDE:
            raise JmpError('资源索引已改变，请重新加载资源包')
        path = record[:PATH_FIELD].split(b'\0')[0].decode('latin1')
        if path.lower() != e.path.lower():
            raise JmpError('资源索引与路径不一致，请重新加载资源包')
        off, csize, rsize = struct.unpack_from('<III', record, PATH_FIELD)
        if off < HDR + STRIDE * count or csize == 0 or off + csize > os.fstat(f.fileno()).st_size:
            raise JmpError('资源数据地址或长度越界')
        e.off, e.csize, e.rsize = off, csize, rsize
        e.md5 = record[PATH_FIELD + 12:].decode('ascii')
        return record


class JmpError(Exception):
    pass


@dataclass
class Entry:
    pack: str
    index: int          # 条目序号
    path: str           # ..\data\...
    off: int
    csize: int
    rsize: int
    md5: str

    @property
    def rec(self) -> int:            # 记录起始（= 路径字段起点）
        return HDR + STRIDE * self.index

    @property
    def quad(self) -> int:           # 数字字段位置 = 路径 + 260
        return self.rec + PATH_FIELD

    def short(self) -> str:
        return self.path.replace('..\\data\\', '').replace('\\', '/')


@dataclass
class Pack:
    file: str
    size: int = 0
    count: int = 0
    entries: list = field(default_factory=list)
    parse_ok: bool = False
    error: str = ''
    header: bytes = b''
    read_only: bool = False
    nonstandard_verified: bool = False
    warning: str = ''

    def base_name(self):
        return os.path.basename(self.file)


def parse_pack(path: str, progress=None) -> Pack:
    pk = Pack(file=os.path.abspath(path))
    pk.size = os.path.getsize(path)
    with open(path, 'rb') as f:
        head = f.read(HDR)
        if len(head) < HDR:
            pk.error = '文件小于 54 字节（空占位包）'
            return pk
        pk.header = head[:50]
        unusual = not standard_header(head)
        pk.count = struct.unpack_from('<I', head, 50)[0]
        need = HDR + STRIDE * pk.count
        if need > pk.size:
            pk.error = '资源索引表被截断'
            return pk
        f.seek(HDR)
        buf = f.read(min(STRIDE * pk.count, pk.size - HDR))
    if len(buf) < STRIDE:
        pk.error = '文件过小'
        return pk
    n = min(pk.count, (len(buf)) // STRIDE)
    ents = []
    bad = 0
    for i in range(n):
        b = STRIDE * i
        pathb = buf[b:b + PATH_FIELD]
        nul = pathb.find(b'\x00')
        p = pathb[:nul if nul != -1 else PATH_FIELD]
        off, csize, rsize = struct.unpack_from('<III', buf, b + PATH_FIELD)
        md5b = buf[b + PATH_FIELD + 12:b + STRIDE]
        good = (p[:3] == b'..\\' and all(c in HEXSET for c in md5b.lower())
                and 0 < csize <= 0x20000000 and off >= need and off + csize <= pk.size)
        if not good:
            bad += 1
            if bad > pk.count // 100:
                break
            continue
        ents.append(Entry(pack=pk.file, index=i, path=p.decode('latin1'),
                          off=off, csize=csize, rsize=rsize,
                          md5=md5b.decode('ascii')))
        if progress and i % 5000 == 0:
            progress(pk.base_name(), i, pk.count)
    pk.entries = ents
    pk.parse_ok = len(ents) > 0 and bad <= max(2, pk.count // 50)
    if unusual:
        # Do not treat an unfamiliar/damaged header alone as proof of JMP data.
        # Require every index record and three distributed content checks.
        pk.parse_ok = bool(ents) and not bad and len(ents)==pk.count
        if pk.parse_ok:
            try:
                with open(path,'rb') as f:
                    for i in sorted({0,len(ents)//2,len(ents)-1}):
                        e=ents[i]
                        if e.csize>64*1024*1024:
                            raise JmpError('抽样条目过大，无法自动确认非标准包头')
                        f.seek(e.off);comp=f.read(e.csize)
                        try:
                            decoder=zlib.decompressobj()
                            raw=decoder.decompress(comp,64*1024*1024+1)
                            if len(raw)>64*1024*1024 or not decoder.eof or decoder.unconsumed_tail:
                                raise JmpError('抽样数据解压不完整或过大')
                        except zlib.error:
                            if e.csize!=e.rsize and e.rsize not in (0,0xFFFFFFFF):raise
                            raw=comp
                        if (e.rsize not in (0,0xFFFFFFFF) and len(raw)!=e.rsize) or hashlib.md5(raw).hexdigest()!=e.md5.lower():
                            raise JmpError('抽样条目长度或 MD5 不符')
                pk.nonstandard_verified=True
                pk.warning='JMP 完整索引及抽样内容校验通过；写入时保留原包头并复核目标条目'
            except (OSError,zlib.error,JmpError) as ex:
                pk.parse_ok=False;pk.error='JMP 内容校验失败：%s' % ex
        if not pk.parse_ok:
            pk.entries=[]
            pk.error=pk.error or 'JMP 索引不完整（头部 %s）' % pk.header[:16].hex(' ')
    if not pk.parse_ok:
        pk.error = pk.error or '有效 %d / 坏 %d / 声明 %d' % (len(ents), bad, pk.count)
    return pk


def load_packs(game_dir: str, progress=None) -> list:
    files = sorted(glob.glob(os.path.join(game_dir, 'Data*.jmp')),
                   key=lambda p: (len(os.path.basename(p)), p))
    out = []
    for fp in files:
        try:
            out.append(parse_pack(fp, progress))
        except (JmpError, OSError, struct.error) as e:
            pk = Pack(file=os.path.abspath(fp))
            pk.error = str(e)
            out.append(pk)
    return out


# ---------------------------------------------------------------- 读写

def read_entry(pk: Pack, e: Entry) -> bytes:
    with pack_lock(pk.file), open(pk.file, 'rb') as f:
        refresh_entry(pk, e)
        f.seek(e.off)
        comp = f.read(e.csize)
        if len(comp) != e.csize:
            raise JmpError('资源数据被截断: %s' % e.path)
    try:
        return zlib.decompress(comp)
    except zlib.error:
        # Data8 等 FMOD 包存在 rsize=-1(0xFFFFFFFF) 的直存条目
        if e.csize == e.rsize or e.rsize in (0, 0xFFFFFFFF):
            return comp
        raise JmpError('解压失败: %s' % e.path)


def verify_entry(pk: Pack, e: Entry) -> tuple:
    raw = read_entry(pk, e)
    got = hashlib.md5(raw).hexdigest()
    size_ok = len(raw) == e.rsize or e.rsize in (0, 0xFFFFFFFF)
    return got, (got == e.md5 and size_ok)


def find_entry(pk: Pack, sub: str) -> list:
    s = sub.replace('/', '\\').lower()
    return [e for e in pk.entries if s in e.path.lower()]


def search_all(packs: list, sub: str) -> list:
    out = []
    for pk in packs:
        out.extend(find_entry(pk, sub))
    return out


def _backup_path(backup_dir: str, pk: Pack, e: Entry) -> str:
    tag = hashlib.md5((pk.file + e.path).encode()).hexdigest()[:10]
    os.makedirs(backup_dir, exist_ok=True)
    return os.path.join(backup_dir, 'fix_%s_%d_%s.json'
                        % (pk.base_name(), e.index, tag))


def snapshot(pk: Pack, e: Entry, backup_dir: str) -> str:
    """Keep the first original snapshot; repeated watch updates never replace it."""
    with pack_lock(pk.file):
        bp = _backup_path(backup_dir, pk, e)
        if os.path.exists(bp):
            with open(bp, encoding='utf-8') as f:
                old = json.load(f)
            if old['path'].lower() != e.path.lower() or os.path.normcase(old['pack']) != os.path.normcase(pk.file):
                raise JmpError('备份标识冲突，已停止写入')
            return bp
        record = refresh_entry(pk, e)
        with open(pk.file, 'rb') as f:
            f.seek(e.off)
            data = f.read(e.csize)
        doc = {'time': time.strftime('%Y-%m-%d %H:%M:%S'), 'pack': pk.file,
               'index': e.index, 'path': e.path, 'off': e.off, 'csize': e.csize,
               'rsize': e.rsize, 'md5': e.md5, 'header': pk.header.hex(),
               'record': record.hex(), 'data': data.hex()}
        # Publish only a completely written backup before touching the package.
        fd, temporary = tempfile.mkstemp(prefix='snapshot_', suffix='.tmp', dir=backup_dir)
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                json.dump(doc, f, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temporary, bp)
        finally:
            if os.path.exists(temporary):
                os.remove(temporary)
        return bp


def patch_entry(pk: Pack, e: Entry, new_raw: bytes, backup_dir: str,
                allow_overflow: bool = False) -> dict:
    if not standard_header(pk.header) and not pk.nonstandard_verified:
        raise JmpError('JMP 索引或内容尚未通过完整校验，不能安全写入')
    if pk.nonstandard_verified:
        # Revalidate the exact target before modifying an unfamiliar-header package.
        old_raw = read_entry(pk, e)
        if hashlib.md5(old_raw).hexdigest().lower() != e.md5.lower():
            raise JmpError('JMP 目标条目 MD5 校验失败，不能安全写入')
        if e.rsize not in (0, 0xFFFFFFFF) and len(old_raw) != e.rsize:
            raise JmpError('JMP 目标条目长度校验失败，不能安全写入')
    new_comp = zlib.compress(new_raw, 9)
    new_md5 = hashlib.md5(new_raw).hexdigest()
    with pack_lock(pk.file):
        refresh_entry(pk, e)
        old_size, old_raw_size = e.csize, e.rsize
        if len(new_comp) > old_size and not allow_overflow:
            raise JmpError('新内容压缩后 %dB > 当前空间 %dB' % (len(new_comp), old_size))
        bp = snapshot(pk, e, backup_dir)
        with open(pk.file, 'r+b') as f:
            if len(new_comp) > old_size:
                f.seek(0, os.SEEK_END)
                new_offset = f.tell()
                if new_offset + len(new_comp) > 0xFFFFFFFF:
                    raise JmpError('追加后超过 JMP 32 位地址范围')
            else:
                new_offset = e.off
                f.seek(new_offset)
            f.write(new_comp)
            # Payload first; publish its exact length/address only once flushed.
            f.flush()
            os.fsync(f.fileno())
            f.seek(e.quad)
            f.write(struct.pack('<III', new_offset, len(new_comp), len(new_raw)))
            f.write(new_md5.encode('ascii'))
            f.flush()
            os.fsync(f.fileno())
        e.off, e.csize, e.rsize, e.md5 = new_offset, len(new_comp), len(new_raw), new_md5
        pk.size = os.path.getsize(pk.file)
        return {'backup': bp, 'entry': e.index, 'path': e.path,
                'csize': (old_size, len(new_comp)), 'rsize': (old_raw_size, len(new_raw)),
                'md5': new_md5}


def restore_entry(backup_file: str) -> dict:
    with open(backup_file, encoding='utf-8') as f:
        doc = json.load(f)
    record = bytes.fromhex(doc['record'])
    data = bytes.fromhex(doc['data'])
    if len(record) != STRIDE or len(data) != doc['csize']:
        raise JmpError('备份记录或数据长度不完整')
    off, csize, rsize = struct.unpack_from('<III', record, PATH_FIELD)
    if (off, csize, rsize) != (doc['off'], doc['csize'], doc['rsize']):
        raise JmpError('备份元数据与索引不一致')
    rec = HDR + STRIDE * doc['index']
    with pack_lock(doc['pack']), open(doc['pack'], 'r+b') as f:
        head = f.read(HDR)
        saved_header = bytes.fromhex(doc.get('header', '')) if doc.get('header') else b''
        header_ok = standard_header(head) or (len(saved_header) == 50 and head[:50] == saved_header)
        if len(head) != HDR or not header_ok:
            raise JmpError('还原目标不是有效 JMP 包')
        count = struct.unpack_from('<I', head, 50)[0]
        if not 0 <= doc['index'] < count or off < HDR + STRIDE * count:
            raise JmpError('备份索引或数据地址无效')
        if off + len(data) > os.fstat(f.fileno()).st_size:
            raise JmpError('还原目标被截断')
        f.seek(rec)
        current = f.read(STRIDE)
        if current[:PATH_FIELD] != record[:PATH_FIELD]:
            raise JmpError('还原目标资源已改变，请检查包版本')
        f.seek(off)
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
        f.seek(rec)
        f.write(record)
        f.flush()
        os.fsync(f.fileno())
    return doc


def list_backups(backup_dir: str) -> list:
    out = []
    for fp in glob.glob(os.path.join(backup_dir, '**', 'fix_*.json'), recursive=True):
        try:
            with open(fp, encoding='utf-8') as f:
                d = json.load(f)
            d['_file'] = fp
            out.append(d)
        except Exception:
            pass
    out.sort(key=lambda d: d.get('time', ''), reverse=True)
    return out
