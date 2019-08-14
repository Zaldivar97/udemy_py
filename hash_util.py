from hashlib import sha256
from json import dumps


def hash_string_256(string):
    return sha256(string).hexdigest()


def hash_block(block):
    """Encrypt the block content.


    Arguments:
        :block: The block that should be hashed
    """
    # dumps devuelve un json y encode, lo codifica en bytecode, hexdigest es para convertir el hash en bytes en
    # string. Los dicts son estructuras de datos que no toman en cuenta el orden, esto afecta el hash que devuelve y
    # si cambia el orden de un bloque, se tendra un hash distinto, sin embargo la funcion ---dumps--- brinda la
    # funcionalidad de ordenar el dict antes de trabajarlo(sort_keys)).
    hashable_block = block.__dict__.copy()
    hashable_block['transactions'] = [tx.to_ordered_dict() for tx in hashable_block['transactions']]
    return hash_string_256(dumps(hashable_block, sort_keys=True).encode())
    # return '.'.join([str(val) for val in block.values()])
