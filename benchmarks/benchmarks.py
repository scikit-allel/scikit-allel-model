import numpy as np
import dask.array as da
from skallel.model import fn_numpy, fn_dask


class TimeGenotypeArray:
    """Timing benchmarks for genotype array functions."""

    def setup(self):
        self.data = np.random.randint(-1, 4, size=(10000, 1000, 2), dtype="i1")
        self.data_dask = da.from_array(self.data, chunks=(1000, 200, 2))

    def time_is_called_numpy(self):
        fn_numpy.genotype_array_is_called(self.data)

    def time_is_called_dask(self):
        fn_dask.genotype_array_is_called(self.data_dask)

    def time_is_missing_numpy(self):
        fn_numpy.genotype_array_is_missing(self.data)

    def time_is_missing_dask(self):
        fn_dask.genotype_array_is_missing(self.data_dask)

    def time_count_alleles_numpy(self):
        fn_numpy.genotype_array_count_alleles(self.data, max_allele=3)

    def time_count_alleles_dask(self):
        fn_dask.genotype_array_count_alleles(self.data_dask, max_allele=3)
