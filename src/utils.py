

def process_key(k, v):
    if '__' not in k:
        return {k: v}
    
    k1, k2 = k.rsplit('__', 1)
    k2 = '$' + k2
    return process_key(k1, {k2: v})