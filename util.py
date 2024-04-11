import os


class hexdump:
    def __init__(self, buf, base_addr=0x0):
        self.buf = buf
        self.base_addr = base_addr

    def __iter__(self):
        def _printable(x):
            return 32 <= x < 127

        BPL = 16  # 16 bytes per line
        last_line, last_bts = None, None
        for i in range(0, len(self.buf), BPL):
            bts = bytes(self.buf[i : i + BPL])

            if bts == last_bts:
                line = "*"
            else:
                # 23 = 8*2 + (8-1)
                line = "{:08x}  {:23}  {:23}  |{:16}|".format(
                    self.base_addr + i,
                    " ".join(f"{x:02x}" for x in bts[:8]),
                    " ".join(f"{x:02x}" for x in bts[8:]),
                    "".join(chr(x) if _printable(x) else "." for x in bts),
                )

            if line != last_line:
                yield line

            last_line, last_bts = line, bts

    def __str__(self):
        return "\n".join(self)

    def __repr__(self):
        return str(self)
