import numpy as np
import dask.array as da


from . import fn_numpy
from . import fn_dask


class GenotypeArray(object):
    """TODO"""

    def __init__(self, data):
        """TODO"""

        # TODO support hdf5-like data

        # check type
        if isinstance(data, np.ndarray):
            self._fn = fn_numpy
        elif isinstance(data, da.Array):
            self._fn = fn_dask
        else:
            raise TypeError("TODO")

        # check dtype
        if data.dtype != np.dtype("i1"):
            raise TypeError("TODO")

        # check number of dimensions
        if data.ndim != 3:
            raise ValueError("TODO")

        # all good, store data
        self._data = data

    @property
    def data(self):
        """TODO"""
        return self._data

    @property
    def n_variants(self):
        """TODO"""
        return self.data.shape[0]

    @property
    def n_samples(self):
        """TODO"""
        return self.data.shape[1]

    @property
    def ploidy(self):
        """TODO"""
        return self.data.shape[2]

    @property
    def values(self):
        """Deprecated, use the `data` property instead. Provided for
        backwards-compatibility."""
        return self._data

    def is_called(self):
        """TODO"""
        return self._fn.genotype_array_is_called(self.data)

    def is_missing(self):
        """TODO"""
        return self._fn.genotype_array_is_missing(self.data)

    def is_hom(self):
        """TODO"""
        # TODO support allele argument
        return self._fn.genotype_array_is_hom(self.data)

    # TODO is_het
    # TODO is_call
    # TODO to_n_ref
    # TODO to_n_alt
    # TODO to_allele_counts
    # TODO to_haplotypes
    # TODO __repr__
    # TODO display
    # TODO map_alleles
    # TODO max

    def count_alleles(self, max_allele):
        """TODO"""
        # TODO support subpop arg
        # TODO wrap the result as AlleleCountsArray
        return self._fn.genotype_array_count_alleles(self.data, max_allele)

    # TODO __getitem__ with support for simple slices and/or ints only
    # TODO select_variants_by_id
    # TODO select_variants_by_position
    # TODO select_variants_by_region
    # TODO select_variants_by_index
    # TODO select_variants_by_mask
    # TODO select_samples_by_id
    # TODO select_samples_by_index
    # TODO select_samples_by_mask
    # TODO take
    # TODO compress
    # TODO concatenate


# TODO HaplotypeArray
# TODO n_variants
# TODO n_haplotypes
# TODO __getitem__
# TODO take
# TODO compress
# TODO concatenate
# TODO is_called
# TODO is_missing
# TODO is_ref
# TODO is_alt
# TODO is_call
# TODO to_genotypes
# TODO count_alleles
# TODO map_alleles
# TODO prefix_argsort
# TODO distinct
# TODO distinct_counts
# TODO distinct_frequencies
# TODO display
# TODO __repr__


# TODO AlleleCountsArray
# TODO __add__
# TODO __sub__
# TODO n_variants
# TODO n_alleles
# TODO __getitem__
# TODO compress
# TODO take
# TODO concatenate
# TODO to_frequencies
# TODO allelism
# TODO max_allele
# TODO is_variant
# TODO is_non_variant
# TODO is_segregating
# TODO is_non_segregating
# TODO is_singleton
# TODO is_doubleton
# TODO is_biallelic
# TODO is_biallelic_01
# TODO map_alleles
# TODO display
# TODO __repr__


# TODO GenotypeAlleleCountsArray


# TODO Callset
# TODO __getitem__


# TODO ContigCallset
# TODO __getitem__
# TODO select_variants_by_id
# TODO select_variants_by_position
# TODO select_variants_by_region
# TODO select_variants_by_index
# TODO select_variants_by_mask
# TODO select_samples_by_id
# TODO select_samples_by_index
# TODO select_samples_by_mask
# TODO take
# TODO compress
# TODO concatenate?
