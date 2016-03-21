def encrypt(data, key):
    index = 0
    r = []
    kb = bytearray(key.encode())

    for byte in data:
        a = int(byte)
        p = int(kb[index])
        index = index + 1 if index + 1 < len(kb) else 0
        r.append((a + p) % 256)

    return bytes(r)


def decrypt(data, key):

    index = 0
    r = []
    kb = bytearray(key.encode())

    for byte in data:
        b = int(byte)
        p = int(kb[index])
        index = index + 1 if index + 1 < len(kb) else 0

        d = b - p
        r.append(d if d >= 0 else d + 256)

    return bytes(r)
