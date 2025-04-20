class ObservationElement:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


class TimePicks:
    def __init__(self, time_picks, source_indexes, receiver_indexes):
        self.time_picks = time_picks
        self.source_indexes = source_indexes
        self.receiver_indexes = receiver_indexes


class SeismicRecord:
    def __init__(self, sources, receivers, time_picks):
        self.sources = sources
        self.receivers = receivers
        self.time_picks = time_picks

class ColumnsFile:
    def __init__(self, source_columns, receiver_columns, time_picks_column):
        self.source_columns = source_columns
        self.receiver_columns = receiver_columns
        self.time_picks_column = time_picks_column

