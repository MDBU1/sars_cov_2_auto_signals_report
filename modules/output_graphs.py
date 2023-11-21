import pandas as pd
import plotnine as p9
import plotly.express as px
import datetime
import plotly.graph_objects as go
import json
import warnings

from modules.analysis_signal_mutation_profile import ClassSignalAnalysisMutationProfile


# %%


class ClassOutputGraphs(ClassSignalAnalysisMutationProfile):
    def __init__(self, class_signal):
        super().__init__(class_signal)
        if self.logging_level == "INFO" or "DEBUG":
            warnings.filterwarnings("ignore", module="plotnine\..*")  # disable annoying plotnine warnings
        self.signal_row = self.meth_generate_lineage_percentage_fig()
        self.meth_generate_epi_curve()
        self.meth_generate_period_cumulative_epi_curve()
        self.meth_generate_regional_percentage_epi_curves()
        self.val_loss_map_seqs = self.meth_select_and_generate_map()
        # self.meth_generate_subplot_total_and_percentage_epi_curves()

    def meth_return_graph_ticks(self):
        limits = (pd.to_datetime(self.date_min) - pd.to_timedelta(4, unit='d'), self.date_max)
        breaks = pd.date_range(*limits, freq="W-SUN")
        labels = breaks[0:]
        return limits, breaks, labels

    def meth_generate_lineage_percentage_fig(self):
        self.logger.info("generating lineage percentage fig.")

        #  pull out signal row from all lineage data
        signal_row = self.df_lineage_perc_mod[self.df_lineage_perc_mod["index"].str.contains("SIGNAL")]
        # add signal row top filtered top 25 data, create df temp_df as copy so not assigning same name -> error
        temp_df = self.df_lineage_perc_mod_top.copy()
        temp_df = self.df_lineage_perc_mod_top.append(signal_row)
        temp_df = temp_df.drop("level_0", axis=1)
        # remove duplicate row entries, i.e. if signal already in top 25 data
        temp_df = temp_df.drop_duplicates()
        # round to 5 dp
        temp_df["mod_lineage"] = temp_df["mod_lineage"].round(4)

        # highlight signal -> 20221208 not working so swapped color to mod_lineage
        default_color = "blue"
        colors = {"SIGNAL": "red"}
        color_discrete_map = {
            c: colors.get(c, default_color)
            for c in temp_df.index.unique()}
        # color_discrete_map = {'mod_lineage': 'rgb(255,0,0)'}
        # create int. of total circulating lineage proportions (incl. signal)
        fig_lineage_perc = px.bar(temp_df,
                                  x="index",
                                  y="mod_lineage",
                                  title="Signal (Total Dataset) Compared Against Top 10 Circulating Lineages as of "
                                        + datetime.datetime.now().strftime('%Y%m%d'),
                                  labels={"index": "", "mod_lineage": "Percentage"},
                                  height=400,
                                  text_auto=True,
                                  color="mod_lineage",
                                  color_discrete_map=color_discrete_map
                                  )
        fig_lineage_perc.update_traces(showlegend=False)
        # save figure
        fig_lineage_perc.write_image(self.path_save_dir + "/" + "fig_lineage_percentages.png",
                                     format="png")
        temp_df.to_csv(self.path_save_dir + "/" + "fig_lineage_percentages.csv", index=False)
        return signal_row

    def meth_generate_epi_curve(self):
        # set variables for lineage and mutations to match input
        temp_df = self.df_filtered_country_continent_val.copy()
        if self.data_region == "eng":
            temp_df["fill_data"] = temp_df["usher_lineage"]
            custom_name = "location"
            dataset = "Eng. PHEC Regions Lineages"
        elif self.data_region == "int":
            temp_df["fill_data"] = temp_df["location"]
            custom_name = "location"
            dataset = "International Top 5 Countries per Continent"
        self.logger.info("generating epi curve")

        # limits = (pd.to_datetime(self.date_min) - pd.to_timedelta(4, unit='d'), self.date_max)
        # breaks = pd.date_range(*limits, freq="W-SUN")
        # labels = breaks[0:]
        limits, breaks, labels = self.meth_return_graph_ticks()
        y_breaks = range(0, len(temp_df))

        # create dummy column and data to reset colour codes per region
        list_region = []
        for region in temp_df["region_totals"].unique():
            df1 = temp_df[temp_df["region_totals"].eq(region)]
            df1 = df1.assign(graph_no=df1.groupby("country").ngroup())
            list_region.append(df1)

        temp_df1 = pd.concat(list_region)
        temp_df2 = temp_df1[temp_df1['fill_data'].notna()]

        fig_epi = (p9.ggplot(temp_df2, p9.aes(x="week_beginning", y=1, fill="fill_data", label="id"))
                   + p9.geom_bar(position="stack", stat="identity")
                   + p9.theme_bw()
                   # + p9.scale_fill_brewer(type="qual", palette="Set2")#, name="graph_no")
                   # + p9.scale_fill_brewer(type="qual", palette="Greys")
                   # + p9.scale_alpha_manual(values=(1.0, 0.8, 0.6, 0.4, 0.2))
                   + p9.theme(panel_grid_major_y=p9.element_line(color='gray', size=0.5),
                              panel_grid_minor=p9.element_blank(), panel_grid_major_x=p9.element_blank())
                   + p9.scale_x_date(limits=limits,
                                     breaks=breaks.astype('str').tolist(),
                                     labels=labels.astype('str').tolist())
                   + p9.theme(axis_text_x=p9.element_blank(),
                              figure_size=(25, 5),
                              axis_text=p9.element_text(size=12),
                              legend_text=p9.element_text(size=10),
                              legend_title=p9.element_blank(),
                              legend_direction="horizontal",
                              legend_position=(0.7, 1.05),
                              legend_box_spacing=0.4,
                              legend_margin=-10,
                              plot_title=p9.element_text(ha='left', x=0.15))
                   # + p9.scale_y_continuous(breaks=y_breaks)
                   + p9.xlab("")
                   + p9.ylab("No. Sequences")
                   + p9.guides(fill=p9.guide_legend(nrow=5))
                   + p9.stat_summary(p9.aes(label='stat(y)', group=1), fun_y=sum, geom="text", size=12)
                   + p9.ggtitle(f"A) Weekly EPI-Curve \n "
                                # f"Signal: {self.signal_no}, {self.lineage}, {self.mutations} \n"
                                f"{dataset}, {self.date_min.date()} - {self.date_max.date()}")
                   + p9.facet_wrap("region_totals", nrow=1))
        # + p9.theme(figure_size=(15, 15)))

        p9.ggsave(plot=fig_epi,
                  filename="fig_epi_curve.png",
                  path=self.path_save_dir)
        temp_df.to_csv(self.path_save_dir + "/" + "fig_epi_curve.csv", index=False)
        self.df_filtered_signal.to_csv(self.path_save_dir + "/" + "test.csv", index=False)
        return fig_epi

    def meth_generate_period_cumulative_epi_curve(self):
        temp_df = self.df_filtered_signal_proportion_overall.copy()
        self.logger.info("generating cumulative epi curves")
        limits, breaks, labels = self.meth_return_graph_ticks()

        fig_prop_epi = (p9.ggplot(temp_df, p9.aes(x="date", y="percentage_total"))
                        + p9.geom_bar(stat="identity", fill="darkcyan")
                        + p9.theme_bw(base_size=20)
                        + p9.xlab("")
                        + p9.ylab("Percentage Total Samples")
                        + p9.scale_x_date(limits=limits,
                                          breaks=breaks.astype('str').tolist(),
                                          labels=labels.astype('str').tolist())
                        + p9.theme(axis_text_x=p9.element_text(angle=90),
                                   figure_size=(15, 10))
                        + p9.ggtitle("Percentage Cumulative Epi Curve"))

        p9.ggsave(plot=fig_prop_epi,
                  filename="fig_weekly_cumulative_epi.png",
                  path=self.path_save_dir)
        temp_df.to_csv(self.path_save_dir + "/fig_weekly_cumulative_epi.csv", index=False)

    def meth_generate_regional_percentage_epi_curves(self):
        temp_df_signal = self.df_filtered_signal_proportion_region.copy()
        temp_df_full = self.df_filtered.copy()

        temp_df_full["signal_check"] = temp_df_full["id"].isin(temp_df_signal["id"]) * 1
        temp_df_full['date_epi'] = pd.to_datetime(temp_df_full['date']) - pd.to_timedelta(7, unit='d')
        temp_df1 = temp_df_full.groupby(["region_totals", pd.Grouper(key="date_epi", freq='W-SUN')]).agg(
            {"signal_check": pd.Series.sum}).reset_index().sort_values('date_epi')

        temp_df2 = temp_df_full.groupby(["region_totals", pd.Grouper(key="date_epi", freq='W-SUN')]
                                        ).count().reset_index().sort_values('date_epi')

        temp_df4 = pd.merge(temp_df1, temp_df2, how='left', left_on=['region_totals', 'date_epi'],
                            right_on=['region_totals', 'date_epi'])
        # what is this?
        temp_df4["percent"] = (temp_df4["signal_check_x"] / temp_df4["signal_check_y"]) * 100
        temp_df4["percent"] = temp_df4["percent"].round(1)

        limits, breaks, labels = self.meth_return_graph_ticks()

        # delete regions with no signal sequences
        df = temp_df4.copy()
        df1 = df.groupby("region_totals")["percent"].sum().reset_index()
        df1 = df1[df1["percent"].eq(0)]
        df2 = df[~df["region_totals"].isin(df1["region_totals"])]

        if self.data_region == "eng":
            dataset = "UK PHEC Regions"
        elif self.data_region == "int":
            dataset = "International Continents"
        self.logger.info("generating epi curve")

        fig_prop_epi = (p9.ggplot(df2, p9.aes(x="date_epi", y="percent"))
                        + p9.geom_bar(stat="identity",
                                      fill="darkcyan")
                        + p9.theme_bw()
                        + p9.theme(panel_grid_major_y=p9.element_line(color='gray', size=0.5),
                                   panel_grid_minor=p9.element_line(color='gray', size=0.5),
                                   panel_grid_major_x=p9.element_line(color='gray', size=0.5))
                        + p9.xlab("")
                        + p9.ylab("Percentage Signal/Total Seqs. \n")
                        + p9.scale_x_date(limits=limits,
                                          breaks=breaks.astype('str').tolist(),
                                          labels=labels.astype('str').tolist())
                        + p9.theme(axis_text_x=p9.element_text(angle=90),
                                   figure_size=(25, 5),
                                   plot_title=p9.element_text(ha='left', x=0.15))
                        + p9.ggtitle(f"B) Weekly Proportional EPI-Curve, \n"
                                     # f"Signal: {self.signal_no}, {self.lineage}, {self.mutations}  \n"
                                     f"{dataset}, {self.date_min.date()} - {self.date_max.date()}")
                        + p9.stat_summary(p9.aes(label='stat(y)', group=1), fun_y=sum, geom="text", size=12)
                        + p9.facet_wrap("region_totals", nrow=1))

        p9.ggsave(plot=fig_prop_epi,
                  filename="fig_percentage_region_weekly_epi_curves.png",
                  path=self.path_save_dir)
        temp_df4.to_csv(self.path_save_dir + "/fig_percentage_region_weekly_epi_curves.csv")
        return fig_prop_epi

    def meth_generate_subplot_total_and_percentage_epi_curves(self):
        fig_epi = self.meth_generate_epi_curve()
        fig_prop_epi = self.meth_generate_regional_percentage_epi_curves()
        g1 = pw.load_ggplot(figsize=(25, 5))
        g2 = pw.load_ggplot(figsize=(25, 5))
        g1234 = g1 / g2
        g1234.savefig("test.png")

    def meth_generate_map_uk(self):
        temp_df_map = self.df_filtered_signal_proportion_region.copy()
        with open(rf'{self.uk_geojson}') as f:
            json_utla = json.load(f)

        json_utla_area = {}
        for feature in json_utla['features']:
            feature['id'] = feature['properties']['OBJECTID']
            json_utla_area[feature['properties']['CTYUA17NM']] = feature['id']

        # fix known issues with naming of UTLA regions
        temp_df_map["region_code"] = temp_df_map["region_code"].replace("Bournemouth, Christchurch and Poole",
                                                                        "Bournemouth")
        temp_df_map["region_code"] = temp_df_map["region_code"].replace("West Northamptonshire", "Northamptonshire")
        temp_df_map["region_code"] = temp_df_map["region_code"].replace("North Northamptonshire", "Northamptonshire")

        temp_df_map = temp_df_map[temp_df_map["region_code"].notna()]
        temp_df_map = temp_df_map.dropna(subset=["region_code"])
        temp_df_map = temp_df_map[temp_df_map["region_code"].str.contains("nan") == False]
        temp_df_map["sample_id"] = temp_df_map["id"]
        temp_df_map["id"] = temp_df_map["region_code"].apply(lambda x: json_utla_area[x] if x in json_utla_area else 0)
        val_loss_map_seqs = (len(self.df_filtered_signal_proportion_region) - len(temp_df_map))
        temp_df_map = temp_df_map.astype(str)
        temp_df_map = temp_df_map.groupby("region_code").agg({"sample_id": pd.Series.nunique, "id": "max"})[
            ["sample_id", "id"]].reset_index()

        fig_map_totals = px.choropleth_mapbox(temp_df_map,
                                              locations="id",
                                              geojson=json_utla,
                                              color='sample_id',
                                              mapbox_style='white-bg',
                                              labels={"sample_id": "no. Seqs."})
        fig_map_totals.update_layout(title="UK Map of Reported Sequences",
                                     mapbox_style="carto-positron",
                                     mapbox_zoom=5,
                                     mapbox_center={"lat": 53, "lon": -2},
                                     margin=dict(l=0, r=0, t=10, b=10))

        temp_df_map.to_csv(self.path_save_dir + "/region_UTLA_counts.csv",
                           encoding='utf-8', index=False)
        fig_map_totals.write_image(self.path_save_dir + "/map_UTLA_counts.png", format="png", engine="kaleido")
        return val_loss_map_seqs

    def meth_generate_map_int(self):
        temp_df = self.df_filtered_signal.copy()

        temp_df1 = pd.DataFrame(temp_df["country"].value_counts()).reset_index().rename(columns={"index": "country",
                                                                                                 "country": "samples"})
        temp_df2 = pd.DataFrame(temp_df, columns=["country", "region_code"])
        temp_df = temp_df2.merge(temp_df1, on="country")
        temp_df = temp_df.drop_duplicates()
        fig_int_map = go.Figure(data=go.Choropleth(locations=temp_df["region_code"],
                                                   z=temp_df["samples"],
                                                   text=temp_df['country'],
                                                   colorscale="Inferno",
                                                   autocolorscale=False,
                                                   reversescale=True,
                                                   marker_line_color="darkgray",
                                                   marker_line_width=0.5,
                                                   colorbar_title="Samples",
                                                   colorbar={"orientation": "h", "x": 0.5, "yanchor": "middle",
                                                             "y": 0.1}))
        fig_int_map.update_layout({"geo": {"resolution": 50}})
        fig_int_map.update_geos(showocean=True,
                                oceancolor="lightBlue")
        fig_int_map.update_layout(title="INT. Map of Reported Sequences",
                                  title_y=0.9,
                                  title_x=0.5,
                                  geo=dict(showframe=False,
                                           showcoastlines=False,
                                           projection_type="equirectangular"))
        fig_int_map.update_layout(margin=dict(l=5, r=0, t=0, b=0))

        # save image to save dir location
        temp_df.to_csv(self.path_save_dir + "/fig_int_map.csv", index=False)
        fig_int_map.write_image(self.path_save_dir + "/fig_int_map.png")

    def meth_select_and_generate_map(self):
        if self.data_region == "eng":
            val_loss_map_seqs = self.meth_generate_map_uk()
            return val_loss_map_seqs
        elif self.data_region == "int":
            self.meth_generate_map_int()
            return 0
