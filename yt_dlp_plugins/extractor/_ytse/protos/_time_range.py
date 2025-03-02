import typing
import protobug
import math


@protobug.message
class TimeRange:
    start_ticks: typing.Optional[protobug.Int64] = protobug.field(1, default=None) # startTicks
    duration_ticks: typing.Optional[protobug.Int64] = protobug.field(2, default=None)
    timescale: typing.Optional[protobug.Int32] = protobug.field(3, default=None)

    def get_duration_ms(self):
        if not self.duration_ticks or not self.timescale:
            return None

        return math.ceil((self.duration_ticks / self.timescale) * 1000)

    def get_start_ms(self):
        if not self.start_ticks or not self.timescale:
            return None

        return math.ceil((self.start_ticks / self.timescale) * 1000)
