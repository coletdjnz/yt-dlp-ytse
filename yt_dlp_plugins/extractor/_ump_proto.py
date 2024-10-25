from yt_dlp_plugins.extractor._generated.protos import StreamProtectionStatus_pb2, MediaHeader_pb2, SabrError_pb2, SabrRedirect_pb2


StreamProtectionStatus = StreamProtectionStatus_pb2.StreamProtectionStatus.Status


def parse_stream_protection_status(data):
    sps = StreamProtectionStatus_pb2.StreamProtectionStatus()
    sps.ParseFromString(data)
    return sps


def parse_sabr_redirect(data):
    sps = SabrRedirect_pb2.SabrRedirect()
    sps.ParseFromString(data)
    return sps


def parse_media_header(data):
    sps = MediaHeader_pb2.MediaHeader()
    sps.ParseFromString(data)
    return sps


def parse_sabr_error(data):
    sps = SabrError_pb2.SabrError()
    sps.ParseFromString(data)
    return sps


__all__ = ['StreamProtectionStatus', 'parse_stream_protection_status', 'parse_media_header', 'parse_sabr_error', 'parse_sabr_redirect']