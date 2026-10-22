"""Offline calibration-bank copy planner (DATA ONLY; NOT FLASHABLE).

Never patches executable code or checksums. Intended to catch collisions and
validate source provenance before hardware-specific analysis.
"""
from dataclasses import dataclass
import hashlib


@dataclass(frozen=True)
class BankPlan:
    source_start: int
    block_size: int
    stock_destination: int
    tuned_duplicate_destination: int
    fill_byte: int = 0xC3


@dataclass(frozen=True)
class ScaffoldAudit:
    stock_sha256: str
    tuned_sha256: str
    image_sha256: str
    writes: tuple[tuple[int, int], ...]
    executable_unchanged: bool
    checksum_verified: bool = False
    flashable: bool = False


def _nonoverlapping(ranges):
    ordered = sorted(ranges)
    return all(a[1] <= b[0] for a, b in zip(ordered, ordered[1:]))


def build_scaffold(stock: bytes, tuned: bytes, plan: BankPlan) -> tuple[bytes, ScaffoldAudit]:
    """Copy banks only into explicitly verified empty ranges.

    Image bytes will NOT have corrected firmware checksums or switcher code.
    """
    if len(stock) != len(tuned) or not stock:
        raise ValueError('source sizes differ or are empty')
    values=(plan.source_start, plan.block_size, plan.stock_destination,
            plan.tuned_duplicate_destination,plan.fill_byte)
    if any(not isinstance(x,int) or isinstance(x,bool) for x in values):
        raise ValueError('integer offsets expected')
    src,sz,one,three,fill=values
    if sz<=0 or min(src,one,three)<0 or fill not in range(256):
        raise ValueError('invalid location, block size or fill')
    if max(src,one,three)+sz>len(stock):
        raise ValueError('block outside image')
    if (one-src)%sz or (three-src)%sz:
        raise ValueError('bank locations do not share the same block phase')
    if not _nonoverlapping(((src,src+sz),(one,one+sz),(three,three+sz))):
        raise ValueError('overlapping banks')
    # Reject hidden code edits; only one source calibration bank may differ.
    if stock[:src]!=tuned[:src] or stock[src+sz:]!=tuned[src+sz:]:
        raise ValueError('firmware differs outside the declared calibration source')
    for at in (one,three):
        if any(x!=fill for x in stock[at:at+sz]):
            raise ValueError('destination is not fully empty')
        if any(x!=fill for x in tuned[at:at+sz]):
            raise ValueError('tuned destination is not fully empty')
    candidate=bytearray(tuned)
    candidate[one:one+sz]=stock[src:src+sz]
    candidate[three:three+sz]=tuned[src:src+sz]
    output=bytes(candidate)
    for x in range(len(output)):
        if not (one<=x<one+sz or three<=x<three+sz) and output[x]!=tuned[x]:
            raise AssertionError('out-of-bank modification')
    sha=lambda data:hashlib.sha256(data).hexdigest()
    return output,ScaffoldAudit(sha(stock),sha(tuned),sha(output),
                                tuple(sorted(((one,one+sz),(three,three+sz)))),True)
