# -*- coding: utf-8 -*-
from cellrank.tools import Lineage
from cellrank.tools._utils import _create_categorical_colors

import pytest
import numpy as np
import matplotlib.colors as colors


class TestLineageCreation:
    def test_creation(self):
        x = np.random.random((10, 3))
        names = ["foo", "bar", "baz"]
        colors = ["#000000", "#ababab", "#ffffff"]
        l = Lineage(x, names=names, colors=colors)

        np.testing.assert_array_equal(l, x)
        np.testing.assert_array_equal(l.names, np.array(names))
        np.testing.assert_array_equal(l.colors, np.array(colors))

    def test_wrong_number_of_dimensions(self):
        with pytest.raises(ValueError):
            _ = Lineage(
                np.random.random((10, 3, 1)),
                names=["foo", "bar", "baz"],
                colors=[(0, 0, 0), "#ffffff", "#ff00FF"],
            )

    def test_names_length_mismatch(self):
        with pytest.raises(ValueError):
            _ = Lineage(
                np.random.random((10, 3)),
                names=["foo", "bar"],
                colors=[(0, 0, 0), (0.5, 0.5, 0.5), "foobar"],
            )

    def test_colors_length_mismatch(self):
        with pytest.raises(ValueError):
            _ = Lineage(
                np.random.random((10, 3)),
                names=["foo", "bar", "baz"],
                colors=[(0, 0, 0), (0.5, 0.5, 0.5)],
            )

    def test_wrong_colors(self):
        with pytest.raises(ValueError):
            _ = Lineage(
                np.random.random((10, 3)),
                names=["foo", "bar", "baz"],
                colors=[(0, 0, 0), (0.5, 0.5, 0.5), "foobar"],
            )

    def test_colors_setter(self):
        l = Lineage(
            np.random.random((10, 3)),
            names=["foo", "bar", "baz"],
            colors=[(0, 0, 0), (0.5, 0.5, 0.5), (1, 1, 1)],
        )

        colors = ["#ffffff", "#ffffff", "#ffffff"]
        l.colors = colors

        np.testing.assert_array_equal(l.colors, np.array(colors))

    def test_color_setter_wrong_colors(self):
        l = Lineage(
            np.random.random((10, 3)),
            names=["foo", "bar", "baz"],
            colors=[(0, 0, 0), (0.5, 0.5, 0.5), (1, 1, 1)],
        )

        with pytest.raises(ValueError):
            l.colors = ["#ffffff", "#ffffff", "foo"]

    def test_names_setter(self):
        l = Lineage(
            np.random.random((10, 3)),
            names=["foo", "bar", "baz"],
            colors=[(0, 0, 0), (0.5, 0.5, 0.5), (1, 1, 1)],
        )

        names = ["foo1", "bar1", "baz1"]
        l.names = names

        np.testing.assert_array_equal(l.names, np.array(names))

    def test_names_setter_wrong_type(self):
        l = Lineage(
            np.random.random((10, 3)),
            names=["foo", "bar", "baz"],
            colors=[(0, 0, 0), (0.5, 0.5, 0.5), (1, 1, 1)],
        )

        with pytest.raises(TypeError):
            l.names = ["foo1", "bar1", 3]

    def test_names_setter_wrong_size(self):
        l = Lineage(
            np.random.random((10, 3)),
            names=["foo", "bar", "baz"],
            colors=[(0, 0, 0), (0.5, 0.5, 0.5), (1, 1, 1)],
        )

        with pytest.raises(ValueError):
            l.names = ["foo1", "bar1"]

    def test_names_setter_non_unique(self):
        l = Lineage(
            np.random.random((10, 3)),
            names=["foo", "bar", "baz"],
            colors=[(0, 0, 0), (0.5, 0.5, 0.5), (1, 1, 1)],
        )

        with pytest.raises(ValueError):
            l.names = ["foo1", "bar1", "bar1"]

    def test_non_unique_names(self):
        with pytest.raises(ValueError):
            _ = Lineage(
                np.random.random((10, 3, 1)),
                names=["foo", "bar", "baz"],
                colors=[(0, 0, 0), "#ffffff", "#ff00FF"],
            )


class TestLineageAccessor:
    def test_subset_same_instance(self):
        x = np.random.random((10, 3))
        l = Lineage(
            x,
            names=["foo", "bar", "baz"],
            colors=[(0, 0, 0), (0.5, 0.5, 0.5), (1, 1, 1)],
        )

        y = l[0, 0]

        assert isinstance(y, Lineage)

    def test_singleton_column(self):
        x = np.random.random((10, 3))
        l = Lineage(
            x,
            names=["foo", "bar", "baz"],
            colors=[(0, 0, 0), (0.5, 0.5, 0.5), (1, 1, 1)],
        )

        y = l[:, 0]

        np.testing.assert_array_equal(x[:, 0], np.array(y)[:, 0])

    def test_singleton_column_name(self):
        x = np.random.random((10, 3))
        l = Lineage(
            x,
            names=["foo", "bar", "baz"],
            colors=[(0, 0, 0), (0.5, 0.5, 0.5), (1, 1, 1)],
        )

        y = l[:, "foo"]

        np.testing.assert_array_equal(x[:, 0], np.array(y)[:, 0])

    def test_singleton_column_first_index_assignment(self):
        x = np.random.random((10, 3))
        l = Lineage(
            x,
            names=["foo", "bar", "baz"],
            colors=[(0, 0, 0), (0.5, 0.5, 0.5), (1, 1, 1)],
        )

        y = l["baz"]

        np.testing.assert_array_equal(x[:, 2], np.array(y)[:, 0])
        np.testing.assert_array_equal(y.names, ["baz"])

    def test_singleton_row_and_column(self):
        x = np.random.random((10, 3))
        l = Lineage(
            x,
            names=["foo", "bar", "baz"],
            colors=[(0, 0, 0), (0.5, 0.5, 0.5), (1, 1, 1)],
        )

        y = l[0, "foo"]

        assert isinstance(l, Lineage)
        assert y.shape == (1, 1)
        assert x[0, 0] == y[0, 0]

    def test_mixed_columns(self):
        x = np.random.random((10, 3))
        l = Lineage(
            x,
            names=["foo", "bar", "baz"],
            colors=[(0, 0, 0), (0.5, 0.5, 0.5), (1, 1, 1)],
        )

        y = l[0, ["foo", 2, "bar", 0]]

        np.testing.assert_array_equal(x[[[0]], [0, 2, 1, 0]], np.array(y))

    def test_column_invalid_name(self):
        x = np.random.random((10, 3))
        l = Lineage(
            x,
            names=["foo", "bar", "baz"],
            colors=[(0, 0, 0), (0.5, 0.5, 0.5), (1, 1, 1)],
        )

        with pytest.raises(KeyError):
            y = l["quux"]

    def test_row_subset_with_ints(self):
        x = np.random.random((10, 3))
        l = Lineage(
            x,
            names=["foo", "bar", "baz"],
            colors=[(0, 0, 0), (0.5, 0.5, 0.5), (1, 1, 1)],
        )

        y = l[[1, 2, 3], :]

        np.testing.assert_array_equal(x[[1, 2, 3], :], np.array(y))

    def test_row_subset_with_mask(self):
        x = np.random.random((10, 3))
        l = Lineage(
            x,
            names=["foo", "bar", "baz"],
            colors=[(0, 0, 0), (0.5, 0.5, 0.5), (1, 1, 1)],
        )

        mask = np.ones((x.shape[0]), dtype=np.bool)
        mask[:5] = False
        y = l[mask, :]

        np.testing.assert_array_equal(x[mask, :], np.array(y))

    def test_column_subset_with_ints(self):
        x = np.random.random((10, 3))
        l = Lineage(
            x,
            names=["foo", "bar", "baz"],
            colors=[(0, 0, 0), (0.5, 0.5, 0.5), (1, 1, 1)],
        )

        y = l[:, [2, 0]]

        np.testing.assert_array_equal(x[:, [2, 0]], np.array(y))

    def test_column_subset_with_mask(self):
        x = np.random.random((10, 3))
        l = Lineage(
            x,
            names=["foo", "bar", "baz"],
            colors=[(0, 0, 0), (0.5, 0.5, 0.5), (1, 1, 1)],
        )

        mask = np.ones((x.shape[1]), dtype=np.bool)
        mask[0] = False
        y = l[:, mask]

        np.testing.assert_array_equal(x[:, mask], np.array(y))

    def test_column_subset_with_names(self):
        x = np.random.random((10, 3))
        l = Lineage(
            x,
            names=["foo", "bar", "baz"],
            colors=[(0, 0, 0), (0.5, 0.5, 0.5), (1, 1, 1)],
        )

        y = l[:, ["foo", "bar"]]

        np.testing.assert_array_equal(x[:, [0, 1]], np.array(y))

    def test_comb_row_int_col_int(self):
        x = np.random.random((10, 3))
        l = Lineage(
            x,
            names=["foo", "bar", "baz"],
            colors=[(0, 0, 0), (0.5, 0.5, 0.5), (1, 1, 1)],
        )

        y = l[[0, 1], [1, 2]]

        np.testing.assert_array_equal(x[[0, 1], :][:, [1, 2]], np.array(y))

    def test_comb_row_int_col_mask(self):
        x = np.random.random((10, 3))
        l = Lineage(
            x,
            names=["foo", "bar", "baz"],
            colors=[(0, 0, 0), (0.5, 0.5, 0.5), (1, 1, 1)],
        )

        mask = np.ones((x.shape[1]), dtype=np.bool)
        mask[0] = False
        y = l[[0, 1], mask]

        np.testing.assert_array_equal(x[[0, 1], :][:, mask], np.array(y))

    def test_comb_row_int_col_names(self):
        x = np.random.random((10, 3))
        l = Lineage(
            x,
            names=["foo", "bar", "baz"],
            colors=[(0, 0, 0), (0.5, 0.5, 0.5), (1, 1, 1)],
        )

        y = l[[0, 1], "baz"]

        np.testing.assert_array_equal(x[[0, 1], :][:, [2]], np.array(y))

    def test_comb_row_mask_col_int(self):
        x = np.random.random((10, 3))
        l = Lineage(
            x,
            names=["foo", "bar", "baz"],
            colors=[(0, 0, 0), (0.5, 0.5, 0.5), (1, 1, 1)],
        )

        mask = np.ones((x.shape[0]), dtype=np.bool)
        mask[5:] = False
        y = l[mask, 0]

        np.testing.assert_array_equal(x[mask, :][:, [0]], np.array(y))

    def test_comb_row_mask_col_mask(self):
        x = np.random.random((10, 3))
        l = Lineage(
            x,
            names=["foo", "bar", "baz"],
            colors=[(0, 0, 0), (0.5, 0.5, 0.5), (1, 1, 1)],
        )

        row_mask = np.ones((x.shape[0]), dtype=np.bool)
        row_mask[5:] = False
        col_mask = np.ones((x.shape[1]), dtype=np.bool)
        y = l[row_mask, col_mask]

        np.testing.assert_array_equal(x[row_mask, :][:, col_mask], np.array(y))

    def test_comb_row_mask_col_names(self):
        x = np.random.random((10, 3))
        l = Lineage(
            x,
            names=["foo", "bar", "baz"],
            colors=[(0, 0, 0), (0.5, 0.5, 0.5), (1, 1, 1)],
        )

        mask = np.ones((x.shape[0]), dtype=np.bool)
        mask[5:] = False
        y = l[mask, ["baz", "bar"]]

        np.testing.assert_array_equal(x[mask, :][:, [2, 1]], np.array(y))

    def test_reordering(self):
        x = np.random.random((10, 3))
        l = Lineage(
            x, names=["foo", "bar", "baz"], colors=["#ff0000", "#00ff00", "#0000ff"]
        )

        y = l[["baz", "bar", "foo"]]

        np.testing.assert_array_equal(y.names, ["baz", "bar", "foo"])
        np.testing.assert_array_equal(y.colors, ["#0000ff", "#00ff00", "#ff0000"])

    def test_non_trivial_subset(self):
        x = np.random.random((10, 3))
        l = Lineage(
            x, names=["foo", "bar", "baz"], colors=["#ff0000", "#00ff00", "#0000ff"]
        )

        mask = np.ones((x.shape[0]), dtype=np.bool)
        mask[5:] = False
        y = l[mask, :][:, ["baz", "bar", "foo"]]

        np.testing.assert_array_equal(x[:, ::1], y)
        np.testing.assert_array_equal(y.names, ["baz", "bar", "foo"])
        np.testing.assert_array_equal(y.names, ["#0000ff", "#00ff00", "#ff0000"])

    def test_non_trivial_subset(self):
        x = np.random.random((10, 3))
        l = Lineage(
            x, names=["foo", "bar", "baz"], colors=["#ff0000", "#00ff00", "#0000ff"]
        )

        mask = np.ones((x.shape[0]), dtype=np.bool)
        mask[5:] = False
        y = l[mask, ["baz", "bar", "foo"]]
        z = l[mask, :][:, ["baz", "bar", "foo"]]

        np.testing.assert_array_equal(y, z)
        np.testing.assert_array_equal(y, x[mask, :][:, [2, 1, 0]])
        np.testing.assert_array_equal(y.names, z.names)
        np.testing.assert_array_equal(y.colors, z.colors)

    def test_col_order(self):
        x = np.random.random((10, 5))
        l = Lineage(
            x,
            names=["foo", "bar", "baz", "quux", "wex"],
            colors=["#ff0000", "#00ff00", "#0000ff", "#aaaaaa", "#bbbbbb"],
        )

        y = l[["wex", "quux"]]

        np.testing.assert_array_equal(x[:, [4, 3]], y)
        np.testing.assert_array_equal(y.names, ["wex", "quux"])
        np.testing.assert_array_equal(y.colors, ["#bbbbbb", "#aaaaaa"])

    def test_automatic_color_assignment(self):
        x = np.random.random((10, 3))
        l = Lineage(x, names=["foo", "bar", "baz"])

        gt_colors = [colors.to_hex(c) for c in _create_categorical_colors(3)]

        np.testing.assert_array_equal(l.colors, gt_colors)
