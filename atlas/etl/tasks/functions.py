def chunker(seq, size):
    """Split big list into parts.

    https://stackoverflow.com/a/434328/10265880
    """
    return (seq[pos : pos + size] for pos in range(0, len(seq), size))
