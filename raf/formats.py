from construct import *
import six

def LastOf(*subcons):
    """
    Create an adapter which uses only the last construct.

    If first argument is a string it will be the name.

    """
    name = "seq"
    if isinstance(subcons[0], six.string_types):
        name = subcons[0]
        subcons = subcons[1:]
    return IndexingAdapter(Sequence(name, *subcons), -1)

RAF_INDEX = Struct("header",
    Magic(b"\xF0\x0E\xBE\x18"),
    ULInt32("version"),
    ULInt32("managerIndex"),
    ULInt32("offsetFileList"),
    ULInt32("pathsOffset"),
    Pointer(this.offsetFileList,
        LastOf("files",
            ULInt32("count"),
            Array(this.count,
                Struct("fileEntry",
                    ULInt32("pathHash"),
                    ULInt32("dataOffset"),
                    ULInt32("dataSize"),
                    ULInt32("pathIndex"),
                ),
            ),
        ),
    ),
    Pointer(this.pathsOffset,
        LastOf("paths",
            ULInt32("size"),
            ULInt32("count"),
            Array(this.count,
                LastOf(
                    ULInt32("stringOffset"),
                    ULInt32("stringLength"),
                    Pointer(this._._.pathsOffset + this.stringOffset,
                        CString("stringValue", encoding='utf8'),
                    ),
                ),
            ),
        ),
    ),
)
