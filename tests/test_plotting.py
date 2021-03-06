# -*- coding: utf-8 -*-
from matplotlib.testing import setup
from matplotlib.testing.compare import compare_images
from typing import Union
from pathlib import Path
from anndata import AnnData
from cellrank.tools import MarkovChain

from _helpers import create_model, resize_images_to_same_sizes

import os
import cellrank as cr
import scvelo as scv
import matplotlib.cm as cm
import pytest

setup()

HERE: Path = Path(__file__).parent
GT_FIGS = HERE / "_ground_truth_figures"
FIGS = HERE / "figures"
DPI = 40
TOL = 150

cr.settings.figdir = FIGS
scv.settings.figdir = str(FIGS)

from packaging import version

try:
    from importlib_metadata import version as get_version
except ImportError:
    from importlib.metadata import version as get_version

scvelo_version = pytest.mark.skipif(
    version.parse(get_version(scv.__name__)) < version.parse("0.1.26"),
    reason="scVelo <= 0.1.25 doesn't support node_color for PAGA",
)
del version, get_version


def compare(
    *,
    kind: str = "adata",
    backward: bool = False,
    dirname: Union[str, Path] = None,
    tol: int = TOL,
):
    def _compare_images(expected_path: Union[str, Path], actual_path: Union[str, Path]):
        resize_images_to_same_sizes(expected_path, actual_path)
        res = compare_images(expected_path, actual_path, tol=tol)
        assert res is None, res

    def compare_fwd(
        func
    ):  # mustn't use functools.wraps - it think's `adata` is fixture
        def decorator(self, adata_mc_fwd):
            adata, mc = adata_mc_fwd
            fpath = f"{func.__name__.replace('test_', '')}.png"
            path = fpath[7:] if fpath.startswith("scvelo_") else fpath
            func(self, adata if kind == "adata" else mc, path)

            if dirname is not None:
                for file in os.listdir(FIGS / dirname):
                    _compare_images(GT_FIGS / dirname / file, FIGS / dirname / file)
            else:
                _compare_images(GT_FIGS / fpath, FIGS / fpath)

        return decorator

    def compare_bwd(func):
        def decorator(self, adata_mc_bwd):
            adata, mc = adata_mc_bwd
            fpath = f"{func.__name__.replace('test_', '')}.png"
            path = fpath[7:] if fpath.startswith("scvelo_") else fpath
            func(self, adata if kind == "adata" else mc, path)

            if dirname is not None:
                for file in os.listdir(FIGS / dirname):
                    _compare_images(GT_FIGS / dirname / file, FIGS / dirname / file)
            else:
                _compare_images(GT_FIGS / fpath, FIGS / fpath)

        return decorator

    if kind not in ("adata", "mc"):
        raise ValueError(
            f"Invalid kind `{kind!r}`. Valid options are `'adata'`, `'mc'`."
        )

    if backward:
        return compare_bwd
    return compare_fwd


class TestClusterFates:
    @compare()
    def test_bar(self, adata: AnnData, fpath: Path):
        cr.pl.cluster_fates(adata, "clusters", dpi=DPI, save=fpath)

    @compare()
    def test_bar_cluster_subset(self, adata: AnnData, fpath: Path):
        cr.pl.cluster_fates(
            adata, "clusters", clusters=["Astrocytes", "GABA"], dpi=DPI, save=fpath
        )

    @compare()
    def test_bar_lineage_subset(self, adata: AnnData, fpath: Path):
        cr.pl.cluster_fates(adata, "clusters", lineages=["0"], dpi=DPI, save=fpath)

    @compare(tol=250)
    def test_paga_pie(self, adata: AnnData, fpath: Path):
        cr.pl.cluster_fates(adata, "clusters", mode="paga_pie", dpi=DPI, save=fpath)

    @scvelo_version
    @compare()
    def test_paga_pie_embedding(self, adata: AnnData, fpath: Path):
        cr.pl.cluster_fates(
            adata, "clusters", mode="paga_pie", basis="umap", dpi=DPI, save=fpath
        )

    @compare()
    def test_paga(self, adata: AnnData, fpath: Path):
        cr.pl.cluster_fates(adata, "clusters", mode="paga", dpi=DPI, save=fpath)

    @compare()
    def test_paga_lineage_subset(self, adata: AnnData, fpath: Path):
        cr.pl.cluster_fates(
            adata, "clusters", mode="paga", lineages=["0"], dpi=DPI, save=fpath
        )

    @compare()
    def test_violin(self, adata: AnnData, fpath: Path):
        cr.pl.cluster_fates(adata, "clusters", mode="violin", dpi=DPI, save=fpath)

    @compare()
    def test_violin_cluster_subset(self, adata: AnnData, fpath: Path):
        cr.pl.cluster_fates(adata, "clusters", mode="violin", dpi=DPI, save=fpath)

    @compare()
    def test_violin_lineage_subset(self, adata: AnnData, fpath: Path):
        cr.pl.cluster_fates(
            adata, "clusters", mode="violin", lineages=["1"], dpi=DPI, save=fpath
        )


class TestClusterLineages:
    @compare()
    def test_cluster_lineage(self, adata: AnnData, fpath: Path):
        model = create_model(adata)
        cr.pl.cluster_lineage(
            adata,
            model,
            adata.var_names[:10],
            "0",
            time_key="latent_time",
            dpi=DPI,
            save=fpath,
        )

    @compare()
    def test_cluster_lineage_no_norm(self, adata: AnnData, fpath: Path):
        model = create_model(adata)
        cr.pl.cluster_lineage(
            adata,
            model,
            adata.var_names[:10],
            "0",
            time_key="latent_time",
            norm=False,
            dpi=DPI,
            save=fpath,
        )

    @compare()
    def test_cluster_lineage_data_key(self, adata: AnnData, fpath: Path):
        model = create_model(adata)
        cr.pl.cluster_lineage(
            adata,
            model,
            adata.var_names[:10],
            "0",
            time_key="latent_time",
            data_key="Ms",
            norm=False,
            dpi=DPI,
            save=fpath,
        )


class TestHeatmap:
    @compare()
    def test_heatmap_lineages(self, adata: AnnData, fpath: Path):
        model = create_model(adata)
        cr.pl.heatmap(
            adata,
            model,
            adata.var_names[:10],
            kind="lineages",
            time_key="latent_time",
            dpi=DPI,
            save=fpath,
        )

    @compare()
    def test_heatmap_genes(self, adata: AnnData, fpath: Path):
        model = create_model(adata)
        cr.pl.heatmap(
            adata,
            model,
            adata.var_names[:10],
            kind="genes",
            time_key="latent_time",
            dpi=DPI,
            save=fpath,
        )

    @compare()
    def test_heatmap_cluster_genes(self, adata: AnnData, fpath: Path):
        model = create_model(adata)
        cr.pl.heatmap(
            adata,
            model,
            adata.var_names[:10],
            kind="lineages",
            time_key="latent_time",
            cluster_genes=True,
            dpi=DPI,
            save=fpath,
        )

    @compare()
    def test_heatmap_lineage_height(self, adata: AnnData, fpath: Path):
        model = create_model(adata)
        cr.pl.heatmap(
            adata,
            model,
            adata.var_names[:10],
            kind="lineages",
            time_key="latent_time",
            lineage_height=0.2,
            dpi=DPI,
            save=fpath,
        )

    @compare()
    def test_heatmap_start_end_clusters(self, adata: AnnData, fpath: Path):
        model = create_model(adata)
        cr.pl.heatmap(
            adata,
            model,
            adata.var_names[:10],
            kind="lineages",
            time_key="latent_time",
            start_lineage="0",
            end_lineage="1",
            dpi=DPI,
            save=fpath,
        )

    @compare(tol=250)
    def test_heatmap_cmap(self, adata: AnnData, fpath: Path):
        model = create_model(adata)
        cr.pl.heatmap(
            adata,
            model,
            adata.var_names[:5],
            kind="genes",
            time_key="latent_time",
            cmap=cm.viridis,
            dpi=DPI,
            save=fpath,
        )


class TestGeneTrend:
    @compare(dirname="trends_simple")
    def test_trends(self, adata: AnnData, fpath: Path):
        model = create_model(adata)
        cr.pl.gene_trends(
            adata,
            model,
            adata.var_names[:3],
            data_key="Ms",
            dirname="trends_simple",
            dpi=DPI,
            save=fpath,
        )

    @compare()
    def test_trends_same_plot(self, adata: AnnData, fpath: Path):
        model = create_model(adata)
        cr.pl.gene_trends(
            adata,
            model,
            adata.var_names[:3],
            data_key="Ms",
            same_plot=True,
            dpi=DPI,
            save=fpath,
        )

    @compare()
    def test_trends_hide_cells(self, adata: AnnData, fpath: Path):
        model = create_model(adata)
        cr.pl.gene_trends(
            adata,
            model,
            adata.var_names[0],
            data_key="Ms",
            same_plot=True,
            hide_cells=True,
            dpi=DPI,
            save=fpath,
        )

    @compare()
    def test_trends_conf_int(self, adata: AnnData, fpath: Path):
        model = create_model(adata)
        cr.pl.gene_trends(
            adata,
            model,
            adata.var_names[0],
            data_key="Ms",
            same_plot=True,
            conf_int=False,
            dpi=DPI,
            save=fpath,
        )

    @compare(dirname="trends_sharey")
    def test_trends_sharey(self, adata: AnnData, fpath: Path):
        model = create_model(adata)
        cr.pl.gene_trends(
            adata,
            model,
            adata.var_names[:3],
            data_key="Ms",
            sharey=False,
            dirname="trends_sharey",
            dpi=DPI,
            save=fpath,
        )

    @compare()
    def test_trends_cbar(self, adata: AnnData, fpath: Path):
        model = create_model(adata)
        cr.pl.gene_trends(
            adata,
            model,
            adata.var_names[0],
            data_key="Ms",
            same_plot=True,
            show_cbar=False,
            dpi=DPI,
            save=fpath,
        )

    @compare()
    def test_trends_lineage_cmap(self, adata: AnnData, fpath: Path):
        model = create_model(adata)
        cr.pl.gene_trends(
            adata,
            model,
            adata.var_names[0],
            data_key="Ms",
            same_plot=True,
            lineage_cmap=cm.Set2,
            dpi=DPI,
            save=fpath,
        )

    @compare()
    def test_trends_lineage_cell_color(self, adata: AnnData, fpath: Path):
        model = create_model(adata)
        cr.pl.gene_trends(
            adata,
            model,
            adata.var_names[0],
            data_key="Ms",
            same_plot=True,
            cell_color="red",
            dpi=DPI,
            save=fpath,
        )

    @compare()
    def test_trend_lw(self, adata: AnnData, fpath: Path):
        model = create_model(adata)
        cr.pl.gene_trends(
            adata,
            model,
            adata.var_names[0],
            data_key="Ms",
            same_plot=True,
            lw=10,
            dpi=DPI,
            save=fpath,
        )


class TestGraph:
    @compare()
    def test_graph(self, adata: AnnData, fpath: Path):
        cr.pl.graph(adata, "T_fwd", ixs=range(10), dpi=DPI, save=fpath)

    @compare()
    def test_graph_layout(self, adata: AnnData, fpath: Path):
        cr.pl.graph(adata, "T_fwd", ixs=range(10), layout="umap", dpi=DPI, save=fpath)

    @compare()
    def test_graph_keys(self, adata: AnnData, fpath: Path):
        cr.pl.graph(
            adata,
            "T_fwd",
            ixs=range(10),
            keys=("outgoing", "self_loops"),
            dpi=DPI,
            save=fpath,
        )

    @compare()
    def test_graph_edge_weight_scale(self, adata: AnnData, fpath: Path):
        cr.pl.graph(
            adata, "T_fwd", ixs=range(10), edge_weight_scale=100, dpi=DPI, save=fpath
        )

    @compare()
    def test_graph_show_arrows(self, adata: AnnData, fpath: Path):
        cr.pl.graph(
            adata,
            "T_fwd",
            ixs=range(15),
            show_arrows=False,
            edge_weight_scale=100,
            dpi=DPI,
            save=fpath,
        )

    @compare()
    def test_graph_curved_edges(self, adata: AnnData, fpath: Path):
        cr.pl.graph(
            adata, "T_fwd", ixs=range(10), edge_use_curved=False, dpi=DPI, save=fpath
        )

    @compare()
    def test_graph_labels(self, adata: AnnData, fpath: Path):
        cr.pl.graph(
            adata, "T_fwd", ixs=range(10), labels=range(10), dpi=DPI, save=fpath
        )

    @compare()
    def test_graph_cmap(self, adata: AnnData, fpath: Path):
        cr.pl.graph(
            adata, "T_fwd", ixs=range(10), cont_cmap=cm.inferno, dpi=DPI, save=fpath
        )

    @compare()
    def test_graph_top_n_edges_incoming(self, adata: AnnData, fpath: Path):
        cr.pl.graph(
            adata,
            "T_fwd",
            ixs=range(10),
            top_n_edges=(2, True, "incoming"),
            edge_weight_scale=100,
            dpi=DPI,
            save=fpath,
        )

    @compare()
    def test_graph_top_n_edges_outgoing(self, adata: AnnData, fpath: Path):
        cr.pl.graph(
            adata,
            "T_fwd",
            ixs=range(10),
            top_n_edges=(2, False, "outgoing"),
            edge_weight_scale=100,
            dpi=DPI,
            save=fpath,
        )

    @compare()
    def test_graph_edge_normalize(self, adata: AnnData, fpath: Path):
        cr.pl.graph(
            adata, "T_fwd", ixs=range(10), edge_normalize=True, dpi=DPI, save=fpath
        )

    @compare()
    def test_graph_categorical_key(self, adata: AnnData, fpath: Path):
        cr.pl.graph(
            adata,
            "T_fwd",
            ixs=range(10),
            keys=["clusters"],
            keylocs=["obs"],
            dpi=DPI,
            save=fpath,
        )

    @compare()
    def test_trends_size(self, adata: AnnData, fpath: Path):
        model = create_model(adata)
        cr.pl.gene_trends(
            adata,
            model,
            adata.var_names[0],
            data_key="Ms",
            same_plot=True,
            size=30,
            dpi=DPI,
            save=fpath,
        )

    @compare()
    def test_trends_margins(self, adata: AnnData, fpath: Path):
        model = create_model(adata)
        cr.pl.gene_trends(
            adata,
            model,
            adata.var_names[0],
            data_key="Ms",
            same_plot=True,
            margins=0.2,
            dpi=DPI,
            save=fpath,
        )

    @compare()
    def test_trends_cell_alpha(self, adata: AnnData, fpath: Path):
        model = create_model(adata)
        cr.pl.gene_trends(
            adata,
            model,
            adata.var_names[0],
            data_key="Ms",
            same_plot=True,
            cell_alpha=0,
            dpi=DPI,
            save=fpath,
        )

    @compare()
    def test_trends_lineage_alpha(self, adata: AnnData, fpath: Path):
        model = create_model(adata)
        cr.pl.gene_trends(
            adata,
            model,
            adata.var_names[0],
            data_key="Ms",
            same_plot=True,
            lineage_alpha=1,
            dpi=DPI,
            save=fpath,
        )


class TestMarkovChain:
    @compare(kind="mc")
    def test_mc_eig(self, mc: MarkovChain, fpath: Path):
        mc.plot_eig(dpi=DPI, save=fpath)

    @compare(kind="mc")
    def test_mc_real_spectrum(self, mc: MarkovChain, fpath: Path):
        mc.plot_real_spectrum(dpi=DPI, save=fpath)

    @compare(kind="mc")
    def test_scvelo_eig_embedding_clusters(self, mc: MarkovChain, fpath: Path):
        mc.plot_eig_embedding(cluster_key="clusters", dpi=DPI, save=str(fpath))

    @compare(kind="mc")
    def test_scvelo_eig_embedding_left(self, mc: MarkovChain, fpath: Path):
        mc.plot_eig_embedding(dpi=DPI, save=str(fpath))

    @compare(kind="mc")
    def test_scvelo_eig_embedding_right(self, mc: MarkovChain, fpath: Path):
        mc.plot_eig_embedding(left=False, dpi=DPI, save=str(fpath))

    @compare(kind="mc")
    def test_scvelo_eig_embedding_use_2(self, mc: MarkovChain, fpath: Path):
        mc.plot_eig_embedding(use=2, dpi=DPI, save=str(fpath))

    @compare(kind="mc")
    def test_scvelo_approx_rcs(self, mc: MarkovChain, fpath: Path):
        mc.plot_approx_rcs(dpi=DPI, save=str(fpath))

    @compare(kind="mc")
    def test_scvelo_approx_rcs_clusters(self, mc: MarkovChain, fpath: Path):
        mc.plot_approx_rcs(cluster_key="clusters", dpi=DPI, save=str(fpath))

    @compare(kind="mc")
    def test_scvelo_lin_probs(self, mc: MarkovChain, fpath: Path):
        mc.plot_lin_probs(dpi=DPI, save=str(fpath))

    @compare(kind="mc")
    def test_scvelo_lin_probs_clusters(self, mc: MarkovChain, fpath: Path):
        mc.plot_lin_probs(cluster_key="clusters", dpi=DPI, save=str(fpath))

    @compare(kind="mc")
    def test_scvelo_lin_probs_cmap(self, mc: MarkovChain, fpath: Path):
        mc.plot_lin_probs(cmap=cm.inferno, dpi=DPI, save=str(fpath))

    @compare(kind="mc")
    def test_scvelo_lin_probs_lineages(self, mc: MarkovChain, fpath: Path):
        mc.plot_lin_probs(lineages=["0"], dpi=DPI, save=str(fpath))

    @compare(kind="mc")
    def test_scvelo_lin_probs_time(self, mc: MarkovChain, fpath: Path):
        mc.plot_lin_probs(mode="time", dpi=DPI, save=str(fpath))


class TestLineages:
    @compare()
    def test_scvelo_lineages(self, adata: AnnData, fpath: Path):
        cr.pl.lineages(adata, dpi=DPI, save=str(fpath))

    @compare()
    def test_scvelo_lineages_subset(self, adata: AnnData, fpath: Path):
        cr.pl.lineages(adata, lineages=["1"], dpi=DPI, save=str(fpath))

    @compare()
    def test_scvelo_lineages_time(self, adata: AnnData, fpath: Path):
        cr.pl.lineages(adata, mode="time", dpi=DPI, save=str(fpath))

    @compare()
    def test_scvelo_lineages_cmap(self, adata: AnnData, fpath: Path):
        cr.pl.lineages(adata, cmap=cm.inferno, dpi=DPI, save=str(fpath))

    @compare()
    def test_scvelo_lineages_subset(self, adata: AnnData, fpath: Path):
        cr.pl.lineages(adata, cluster_key="clusters", dpi=DPI, save=str(fpath))


class TestSimilarityPlot:
    @compare()
    def test_similarity(self, adata: AnnData, fpath: Path):
        cr.pl.similarity_plot(adata, "clusters", n_samples=10, dpi=DPI, save=fpath)

    @compare()
    def test_similarity_clusters(self, adata: AnnData, fpath: Path):
        cr.pl.similarity_plot(
            adata,
            "clusters",
            n_samples=10,
            clusters=adata.obs["clusters"].cat.categories,
            dpi=DPI,
            save=fpath,
        )

    @compare()
    def test_similarity_cmap(self, adata: AnnData, fpath: Path):
        cr.pl.similarity_plot(
            adata, "clusters", n_samples=10, cmap=cm.inferno, dpi=DPI, save=fpath
        )

    @compare()
    def test_similarity_fontsize(self, adata: AnnData, fpath: Path):
        cr.pl.similarity_plot(
            adata, "clusters", n_samples=10, fontsize=30, dpi=DPI, save=fpath
        )

    @compare()
    def test_similarity_rotation(self, adata: AnnData, fpath: Path):
        cr.pl.similarity_plot(
            adata, "clusters", n_samples=10, rotation=90, dpi=DPI, save=fpath
        )


class TestComposition:
    @compare()
    def test_composition(self, adata: AnnData, fpath: Path):
        cr.pl.composition(adata, "clusters", dpi=DPI, save=fpath)
