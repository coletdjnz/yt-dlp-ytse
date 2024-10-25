import base64
import enum
from yt_dlp.networking import Response


class UMPPart:
    def __init__(self, part_id: int, size: int, data):
        self.part_type = UMPPartType(part_id)
        self.part_id = part_id
        self.size = size
        self.data = data

    def get_b64_str(self) -> str:
        return base64.b64encode(self.data).decode('utf-8')


class UMPParser:
    def __init__(self, response: Response):
        self.response = response

    def _read_varint(self) -> int:
        def varint_size(byte: int) -> int:
            lo = 0
            for i in range(7, 3, -1):
                if byte & (1 << i):
                    lo += 1
                else:
                    break
            return min(lo + 1, 5)

        next_byte = self.response.read(1)

        if len(next_byte) == 0:
            self.response.close()
            return 0

        prefix = next_byte[0]
        size = varint_size(prefix)
        result = 0
        shift = 0

        if size != 5:
            shift = 8 - size
            mask = (1 << shift) - 1
            result |= prefix & mask

        for i in range(1, size):
            byte = self.response.read(1)[0]
            result |= byte << shift
            shift += 8

        return result

    def iter_parts(self):
        while not self.response.closed:
            part_type = self._read_varint()
            part_size = self._read_varint()
            part_data = self.response.read(part_size)
            yield UMPPart(part_type, part_size, part_data)


class UMPPartType(enum.IntEnum):
    UNKNOWN = -1
    ONESIE_HEADER = 10
    ONESIE_DATA = 11
    MEDIA_HEADER = 20
    MEDIA = 21
    MEDIA_END = 22
    LIVE_METADATA = 31
    HOSTNAME_CHANGE_HINT = 32
    LIVE_METADATA_PROMISE = 33
    LIVE_METADATA_PROMISE_CANCELLATION = 34
    NEXT_REQUEST_POLICY = 35
    USTREAMER_VIDEO_AND_FORMAT_DATA = 36
    FORMAT_SELECTION_CONFIG = 37
    USTREAMER_SELECTED_MEDIA_STREAM = 38
    FORMAT_INITIALIZATION_METADATA = 42
    SABR_REDIRECT = 43
    SABR_ERROR = 44
    SABR_SEEK = 45
    RELOAD_PLAYER_RESPONSE = 46
    PLAYBACK_START_POLICY = 47
    ALLOWED_CACHED_FORMATS = 48
    START_BW_SAMPLING_HINT = 49
    PAUSE_BW_SAMPLING_HINT = 50
    SELECTABLE_FORMATS = 51
    REQUEST_IDENTIFIER = 52
    REQUEST_CANCELLATION_POLICY = 53
    ONESIE_PREFETCH_REJECTION = 54
    TIMELINE_CONTEXT = 55
    REQUEST_PIPELINING = 56
    SABR_CONTEXT_UPDATE = 57
    STREAM_PROTECTION_STATUS = 58
    SABR_CONTEXT_SENDING_POLICY = 59
    LAWNMOWER_POLICY = 60
    SABR_ACK = 61
    END_OF_TRACK = 62
    CACHE_LOAD_POLICY = 63
    LAWNMOWER_MESSAGING_POLICY = 64
    PREWARM_CONNECTION = 65

    @classmethod
    def _missing_(cls, value):
        return cls.UNKNOWN


__all__ = ['UMPPart', 'UMPParser']