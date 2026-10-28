"""Structural PE32+ mock ONLY; never execute or ship these test bytes."""

def synthetic_pe64(*, machine=0x8664, signature=b"PE\0\0", opt=0x20B):
    data = bytearray(1024)
    data[:2] = b"MZ"
    data[0x3C:0x40] = (128).to_bytes(4, "little")
    data[128:132] = signature
    data[132:134] = machine.to_bytes(2, "little")
    data[134:136] = (1).to_bytes(2, "little")  # one section
    data[148:150] = (240).to_bytes(2, "little")  # optional-header length
    data[150:152] = (0x0022).to_bytes(2, "little")  # executable, large address aware
    data[152:154] = opt.to_bytes(2, "little")
    data[168:172] = (0x1000).to_bytes(4, "little")  # entry point
    data[184:188] = (0x1000).to_bytes(4, "little")  # section alignment
    data[188:192] = (0x200).to_bytes(4, "little")  # file alignment
    data[208:212] = (0x2000).to_bytes(4, "little")  # image size
    data[212:216] = (0x200).to_bytes(4, "little")  # headers size
    data[220:222] = (2).to_bytes(2, "little")  # GUI subsystem
    section = 392  # NT 128 + 24 + optional 240
    data[section:section + 8] = b".text\0\0\0"
    data[section + 8:section + 12] = (0x180).to_bytes(4, "little")
    data[section + 12:section + 16] = (0x1000).to_bytes(4, "little")
    data[section + 16:section + 20] = (0x200).to_bytes(4, "little")
    data[section + 20:section + 24] = (0x200).to_bytes(4, "little")
    data[section + 36:section + 40] = (0x60000020).to_bytes(4, "little")
    return bytes(data)
