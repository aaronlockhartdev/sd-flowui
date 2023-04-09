from .node import Node

from .load_checkpoint_v1 import LoadCheckpointV1
from .load_checkpoint_v2 import LoadCheckpointV2
from .clip_encode import CLIPEncode

constructors = {
    "LoadCheckpointV1": LoadCheckpointV1,
    "LoadCheckpointV2": LoadCheckpointV2,
    "CLIPEncode": CLIPEncode,
}
