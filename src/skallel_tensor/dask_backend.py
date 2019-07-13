import numbers
import warnings
import numpy as np
import dask.array as da
import dask.dataframe as dd
from . import api, numpy_backend, utils


chunked_array_types = (da.Array,)
try:
    # noinspection PyUnresolvedReferences
    import h5py

    chunked_array_types += (h5py.Dataset,)
except ImportError:  # pragma: no cover
    pass
try:
    # noinspection PyUnresolvedReferences
    import zarr

    chunked_array_types += (zarr.Array,)
except ImportError:  # pragma: no cover
    pass


def ensure_dask_array(a):
    if isinstance(a, da.Array):
        # Pass through.
        return a
    else:
        # Convert to dask array.
        return da.from_array(a)


def ensure_dask_or_numpy_array(a):
    if isinstance(a, np.ndarray):
        # Pass through.
        return a
    else:
        return ensure_dask_array(a)


def select_slice(a, start=None, stop=None, step=None, axis=0):
    a = ensure_dask_array(a)
    item = utils.expand_slice(
        start=start, stop=stop, step=step, axis=axis, ndim=a.ndim
    )
    return a[item]


api.dispatch_select_slice.add((chunked_array_types,), select_slice)


def select_indices(a, indices, axis=0):
    a = ensure_dask_array(a)
    indices = ensure_dask_or_numpy_array(indices)
    return da.take(a, indices, axis=axis)


api.dispatch_select_indices.add(
    (chunked_array_types, np.ndarray), select_indices
)
api.dispatch_select_indices.add(
    (chunked_array_types, chunked_array_types), select_indices
)


def select_mask(a, mask, axis=0):
    a = ensure_dask_array(a)
    mask = ensure_dask_or_numpy_array(mask)
    return da.compress(mask, a, axis=axis)


api.dispatch_select_mask.add((chunked_array_types, np.ndarray), select_mask)
api.dispatch_select_mask.add(
    (chunked_array_types, chunked_array_types), select_mask
)


def concatenate(seq, axis=0):
    seq = [ensure_dask_array(a) for a in seq]
    return da.concatenate(seq, axis=axis)


api.dispatch_concatenate.add((chunked_array_types,), concatenate)


def genotypes_3d_to_called_allele_counts(gt):
    gt = ensure_dask_array(gt)
    out = da.map_blocks(
        numpy_backend.genotypes_3d_to_called_allele_counts,
        gt,
        drop_axis=2,
        dtype=bool,
    )
    return out


api.dispatch_genotypes_3d_to_called_allele_counts.add(
    (chunked_array_types,), genotypes_3d_to_called_allele_counts
)


def genotypes_3d_to_missing_allele_counts(gt):
    gt = ensure_dask_array(gt)
    out = da.map_blocks(
        numpy_backend.genotypes_3d_to_missing_allele_counts,
        gt,
        drop_axis=2,
        dtype=bool,
    )
    return out


api.dispatch_genotypes_3d_to_missing_allele_counts.add(
    (chunked_array_types,), genotypes_3d_to_missing_allele_counts
)


def genotypes_3d_locate_hom(gt):
    gt = ensure_dask_array(gt)
    out = da.map_blocks(
        numpy_backend.genotypes_3d_locate_hom, gt, drop_axis=2, dtype=bool
    )
    return out


api.dispatch_genotypes_3d_locate_hom.add(
    (chunked_array_types,), genotypes_3d_locate_hom
)


def genotypes_3d_locate_het(gt):
    gt = ensure_dask_array(gt)
    out = da.map_blocks(
        numpy_backend.genotypes_3d_locate_het, gt, drop_axis=2, dtype=bool
    )
    return out


api.dispatch_genotypes_3d_locate_het.add(
    (chunked_array_types,), genotypes_3d_locate_het
)


def genotypes_3d_locate_call(gt, call):
    gt = ensure_dask_array(gt)
    out = da.map_blocks(
        numpy_backend.genotypes_3d_locate_call,
        gt,
        call,
        drop_axis=2,
        dtype=bool,
    )
    return out


api.dispatch_genotypes_3d_locate_call.add(
    (chunked_array_types, np.ndarray), genotypes_3d_locate_call
)


def _map_genotypes_3d_count_alleles(chunk, max_allele):

    # Compute allele counts for chunk.
    ac = numpy_backend.genotypes_3d_count_alleles(chunk, max_allele)

    # Insert extra dimension to allow for reducing.
    ac = ac[:, None, :]

    return ac


def genotypes_3d_count_alleles(gt, max_allele):
    gt = ensure_dask_array(gt)

    # Determine output chunks - preserve axis 0; change axis 1, axis 2.
    chunks = (gt.chunks[0], (1,) * len(gt.chunks[1]), (max_allele + 1,))

    # Map blocks and reduce via sum.
    out = da.map_blocks(
        _map_genotypes_3d_count_alleles,
        gt,
        max_allele,
        chunks=chunks,
        dtype="i4",
    ).sum(axis=1, dtype="i4")

    return out


api.dispatch_genotypes_3d_count_alleles.add(
    (chunked_array_types,), genotypes_3d_count_alleles
)


def genotypes_3d_to_allele_counts(gt, max_allele):
    gt = ensure_dask_array(gt)

    # Determine output chunks - preserve axis 0, 1; change axis 2.
    chunks = (gt.chunks[0], gt.chunks[1], (max_allele + 1,))

    # Map blocks.
    out = da.map_blocks(
        numpy_backend.genotypes_3d_to_allele_counts,
        gt,
        max_allele,
        chunks=chunks,
        dtype="i1",
    )

    return out


api.dispatch_genotypes_3d_to_allele_counts.add(
    (chunked_array_types, numbers.Integral), genotypes_3d_to_allele_counts
)


def genotypes_3d_to_allele_counts_melt(gt, max_allele):
    gt = ensure_dask_array(gt)

    # Determine output chunks - change axis 0; preserve axis 1; drop axis 2.
    dim0_chunks = tuple(np.array(gt.chunks[0]) * (max_allele + 1))
    chunks = (dim0_chunks, gt.chunks[1])

    # Map blocks.
    out = da.map_blocks(
        numpy_backend.genotypes_3d_to_allele_counts_melt,
        gt,
        max_allele,
        chunks=chunks,
        dtype="i1",
        drop_axis=2,
    )

    return out


api.dispatch_genotypes_3d_to_allele_counts_melt.add(
    (chunked_array_types, numbers.Integral), genotypes_3d_to_allele_counts_melt
)


def allele_counts_2d_to_frequencies(ac):
    ac = ensure_dask_array(ac)
    out = da.map_blocks(
        numpy_backend.allele_counts_2d_to_frequencies, ac, dtype=np.float32
    )
    return out


api.dispatch_allele_counts_2d_to_frequencies.add(
    (chunked_array_types,), allele_counts_2d_to_frequencies
)


def allele_counts_2d_max_allele(ac):
    ac = ensure_dask_array(ac)
    out = da.map_blocks(
        numpy_backend.allele_counts_2d_max_allele,
        ac,
        dtype=np.int8,
        drop_axis=1,
    )
    return out


api.dispatch_allele_counts_2d_max_allele.add(
    (chunked_array_types,), allele_counts_2d_max_allele
)


def allele_counts_2d_allelism(ac):
    ac = ensure_dask_array(ac)
    out = da.map_blocks(
        numpy_backend.allele_counts_2d_allelism, ac, dtype=np.int8, drop_axis=1
    )
    return out


api.dispatch_allele_counts_2d_allelism.add(
    (chunked_array_types,), allele_counts_2d_allelism
)


def allele_counts_2d_locate_variant(ac):
    ac = ensure_dask_array(ac)
    out = da.map_blocks(
        numpy_backend.allele_counts_2d_locate_variant,
        ac,
        dtype=np.bool_,
        drop_axis=1,
    )
    return out


api.dispatch_allele_counts_2d_locate_variant.add(
    (chunked_array_types,), allele_counts_2d_locate_variant
)


def allele_counts_2d_locate_non_variant(ac):
    ac = ensure_dask_array(ac)
    out = da.map_blocks(
        numpy_backend.allele_counts_2d_locate_non_variant,
        ac,
        dtype=np.bool_,
        drop_axis=1,
    )
    return out


api.dispatch_allele_counts_2d_locate_non_variant.add(
    (chunked_array_types,), allele_counts_2d_locate_non_variant
)


def allele_counts_2d_locate_segregating(ac):
    ac = ensure_dask_array(ac)
    out = da.map_blocks(
        numpy_backend.allele_counts_2d_locate_segregating,
        ac,
        dtype=np.bool_,
        drop_axis=1,
    )
    return out


api.dispatch_allele_counts_2d_locate_segregating.add(
    (chunked_array_types,), allele_counts_2d_locate_segregating
)


def allele_counts_3d_locate_hom(ac):
    ac = ensure_dask_array(ac)
    out = da.map_blocks(
        numpy_backend.allele_counts_3d_locate_hom,
        ac,
        dtype=np.bool_,
        drop_axis=2,
    )
    return out


api.dispatch_allele_counts_3d_locate_hom.add(
    (chunked_array_types,), allele_counts_3d_locate_hom
)


def allele_counts_3d_locate_het(ac):
    ac = ensure_dask_array(ac)
    out = da.map_blocks(
        numpy_backend.allele_counts_3d_locate_het,
        ac,
        dtype=np.bool_,
        drop_axis=2,
    )
    return out


api.dispatch_allele_counts_3d_locate_het.add(
    (chunked_array_types,), allele_counts_3d_locate_het
)


def variants_to_dataframe(variants, columns):

    # Build dataframe.
    df_cols = []
    for c in columns:

        # Obtain values.
        a = variants[c]

        # Check type.
        a = ensure_dask_array(a)

        # Check number of dimensions.
        if a.ndim == 1:
            df_cols.append(a.to_dask_dataframe(columns=c))
        elif a.ndim == 2:
            # Split columns.
            df_cols.append(
                a.to_dask_dataframe(
                    columns=[
                        "{}_{}".format(c, i + 1) for i in range(a.shape[1])
                    ]
                )
            )
        else:
            warnings.warn(
                "Ignoring {!r} because it has an unsupported number of "
                "dimensions.".format(c)
            )

    df = dd.concat(df_cols, axis=1)

    return df


api.dispatch_variants_to_dataframe.add(
    (chunked_array_types,), variants_to_dataframe
)
