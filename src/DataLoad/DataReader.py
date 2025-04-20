import numpy as np
import pandas as pd

from src.DataLoad.scheme.SeismicRecord import SeismicRecord, ObservationElement, TimePicks, ColumnsFile

class DataReader:

    @staticmethod
    def LoadSeisProPick(table_path):
        '''
        Код, для чтение файла в выходном формате SeisPro с модуля picks

        SOU_X:REC_X
            0.0:      0.0      0.0
            0.0:      4.0 12.95045
        '''
        source_columns = ['SP_X']
        receiver_columns = ['RCV_X']
        time_picks_column = ['USER_FBPICK']

        SP_X, RCV_X, USER_FBPICK = [], [], []

        with open(table_path) as f:
            for line in f:
                line = line.strip()
                if not line.startswith('S'):
                    values = list(filter(None, line.split()))
                    try:
                        SP_X.append(float(values[0][:-1]))
                        RCV_X.append(float(values[1]))
                        USER_FBPICK.append(float(values[2]))
                    except (IndexError, ValueError) as e:
                        raise ValueError(f"Ошибка разбора строки. Проверь формат входных файлов.") from e

        table = pd.DataFrame(list(zip(SP_X, RCV_X, USER_FBPICK)), columns = ['SP_X', 'RCV_X', 'USER_FBPICK'])
        table_cols = dict(zip(table.keys().tolist(), np.arange(0, table.shape[1], 1, dtype=int)))
        table = np.asarray(table)

        table_names = ColumnsFile(source_columns, receiver_columns, time_picks_column)

        return table, table_cols, table_names

    @staticmethod
    def LoadSeisProEasy(table_path):
        '''
        Код, для чтение файла в выходном формате SeisPro с модуля easy_refrection

        0	0	100.0598
        0	5	120.078
        0	10	123.378
        0	15	126.118
        '''
        source_columns = ['SP_X']
        receiver_columns = ['RCV_X']
        time_picks_column = ['USER_FBPICK']

        table = pd.read_csv(table_path, sep=r'\s+', names = ['SP_X', 'RCV_X', 'USER_FBPICK'], dtype=float)
        table_cols = dict(zip(table.keys().tolist(), np.arange(0, table.shape[1], 1, dtype=int)))
        table = np.asarray(table)

        table_names = ColumnsFile(source_columns, receiver_columns, time_picks_column)

        return table, table_cols, table_names

    @staticmethod
    def UniqueElements(table, table_columns, columns_names):
        indexes_names = [table_columns.get(name) for name in columns_names]
        table = table[:, indexes_names]
        unique_table, indexes = np.unique(table, axis = 0, return_inverse=True)

        return unique_table, indexes

    @staticmethod
    def LoadTimes(table, table_columns, columns_names):
        indexes_names = [table_columns.get(name) for name in columns_names]
        time_picks = np.asarray(table[:, indexes_names]) / 1000

        return time_picks

    @staticmethod
    def LoadRelief(source_unique, receiver_unique, relief_path = None):

        if relief_path is None:
            SP_Z, RCV_Z = np.linspace(0, 0, len(source_unique)), np.linspace(0, 0, len(receiver_unique))
        else:
            relief_table = pd.read_csv(relief_path, sep=r'\s+', names=['X', 'Z'])
            x_array = np.arange(0, receiver_unique[-1] + 1, 1)
            z_array = np.interp(x_array, relief_table.X.to_numpy(), relief_table.Z.to_numpy())

            SP_Z_index = np.where(x_array[:, np.newaxis] == source_unique)[0]
            RCV_Z_index = np.where(x_array[:, np.newaxis] == receiver_unique)[0]

            SP_Z, RCV_Z = z_array[SP_Z_index], z_array[RCV_Z_index]

        return SP_Z, RCV_Z

    def GetSeisProPick(self, table_path, relief_path):

        # Picks file (SeisPro)
        table, table_nums, table_names = self.LoadSeisProPick(table_path)
        source_unique, source_indexes = self.UniqueElements(table, table_nums, table_names.source_columns)
        receiver_unique, receiver_indexes = self.UniqueElements(table, table_nums, table_names.receiver_columns)
        times = self.LoadTimes(table, table_nums, table_names.time_picks_column)

        # Get releif
        SP_Z, RCV_Z = self.LoadRelief(source_unique, receiver_unique, relief_path = relief_path)
        SP_Y, RCV_Y = None, None

        sources = ObservationElement(source_unique.ravel(), SP_Y, SP_Z)
        receivers = ObservationElement(receiver_unique.ravel(), RCV_Y, RCV_Z)
        time_picks = TimePicks(times.ravel(), source_indexes, receiver_indexes)

        seismic_record = SeismicRecord(sources, receivers, time_picks)

        return seismic_record

    def GetSeisProEasy(self, table_path, relief_path):

        #Easy refraction file (SeisPro)
        table, table_nums, table_names = self.LoadSeisProEasy(table_path)
        source_unique, source_indexes = self.UniqueElements(table, table_nums, table_names.source_columns)
        receiver_unique, receiver_indexes = self.UniqueElements(table, table_nums, table_names.receiver_columns)
        times = self.LoadTimes(table, table_nums, table_names.time_picks_column)

        # Get releif
        SP_Z, RCV_Z = self.LoadRelief(source_unique, receiver_unique, relief_path = relief_path)
        SP_Y, RCV_Y = None, None

        sources = ObservationElement(source_unique.ravel(), SP_Y, SP_Z)
        receivers = ObservationElement(receiver_unique.ravel(), RCV_Y, RCV_Z)
        time_picks = TimePicks(times.ravel(), source_indexes, receiver_indexes)

        seismic_record = SeismicRecord(sources, receivers, time_picks)

        return seismic_record
