import pandas as pd
import plotnine as p9
import os
import plotly.express as px
import datetime
import seaborn as sns
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import json

from modules.analysis_signal_genetic import ClassSignalAnalysisGenetic
import math


# %%


class ClassOutputGraphs(ClassSignalAnalysisGenetic):
    def __init__(self):
        super().__init__()
        self.signal_row = self.meth_generate_lineage_percentage_fig()
        self.meth_generate_epi_curve()
        self.meth_generate_period_cumulative_epi_curve()
        self.meth_generate_regional_percentage_epi_curves()
        self.val_loss_map_seqs = self.meth_select_and_generate_map()

    def meth_return_graph_ticks(self):
        limits = (pd.to_datetime(self.date_min) - pd.to_timedelta(4, unit='d'), self.date_max)
        breaks = pd.date_range(*limits, freq="W-SUN")
        labels = breaks[0:]
        return limits, breaks, labels

    def meth_generate_lineage_percentage_fig(self):
        print("generating lineage percentage fig.")

        #  pull out signal row from all lineage data
        signal_row = self.df_lineage_perc_mod[self.df_lineage_perc_mod["index"].str.contains("SIGNAL")]
        # print(signal_row)
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
        # print(temp_df)
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
        temp_df = self.df_filtered_country_val.copy()
        if self.data_region == "uk":
            temp_df["fill_data"] = temp_df["usher_lineage"]
            custom_name = "location"
            dataset = "UK PHEC Regions"
        elif self.data_region == "int":
            temp_df["fill_data"] = temp_df["location"]
            custom_name = "location"
            dataset = "International Top 5 Countries per Continent"
        self.logger.info("generating epi curve")

        limits = (pd.to_datetime(self.date_min) - pd.to_timedelta(4, unit='d'), self.date_max)
        breaks = pd.date_range(*limits, freq="W-SUN")
        labels = breaks[0:]

        fig_epi = (p9.ggplot(temp_df, p9.aes(x="week_beginning", y=1, fill="fill_data", label="id"))
                   + p9.geom_bar(position="stack", stat="identity")
                   # + p9.theme_bw(base_size=20)
                   # + p9.theme(figure_size=(30, 5))
                   + p9.scale_x_date(limits=limits,
                                     breaks=breaks.astype('str').tolist(),
                                     labels=labels.astype('str').tolist())
                   + p9.theme(axis_text_x=p9.element_text(angle=90),
                              figure_size=(25, 5),
                              axis_text=p9.element_text(size=12),
                              legend_text=p9.element_text(size=12),
                              legend_position="right")
                   + p9.xlab("")
                   + p9.ylab("samples")
                   + p9.guides(fill=p9.guide_legend(title="%s " % custom_name, ncol=1))
                   + p9.stat_summary(p9.aes(label='stat(y)', group=1), fun_y=sum, geom="text", size=12)
                   + p9.ggtitle(f"EPI-Curve {dataset}: Prev. 7 Weeks -> Last Week \n"
                                f"SIGNAL: {self.signal_no}, {self.lineage}, {self.mutations}")
                   + p9.facet_wrap("region_totals", nrow=1))
        # + p9.theme(figure_size=(15, 15)))

        p9.ggsave(plot=fig_epi,
                  filename="fig_epi_curve.png",
                  path=self.path_save_dir)
        temp_df.to_csv(self.path_save_dir + "/" + "fig_epi_curve.csv", index=False)

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

        # bad repeat
        temp_df_full["region_totals"] = temp_df_full.groupby(["region"])["id"].transform(len)
        temp_df_full["region_totals"] = (temp_df_full["region"].astype(str) + ": "
                                         + temp_df_full["region_totals"].astype(str))

        temp_df_full["signal_check"] = temp_df_full["usher_lineage"].isin(temp_df_signal["usher_lineage"]) * 1
        temp_df_full['date_epi'] = pd.to_datetime(temp_df_full['date']) - pd.to_timedelta(7, unit='d')
        temp_df1 = temp_df_full.groupby(["region_totals", pd.Grouper(key="date_epi", freq='W-SUN')]).agg(
            {"signal_check": pd.Series.sum}).reset_index().sort_values('date_epi')

        temp_df2 = temp_df_full.groupby(["region_totals", pd.Grouper(key="date_epi", freq='W-SUN')]
                                        ).count().reset_index().sort_values('date_epi')

        temp_df4 = pd.merge(temp_df1, temp_df2, how='left', left_on=['region_totals', 'date_epi'],
                            right_on=['region_totals', 'date_epi'])

        temp_df4["percent"] = (temp_df4["signal_check_x"] / temp_df4["signal_check_y"]) * 100
        temp_df4["percent"] = temp_df4["percent"].round(2)

        limits, breaks, labels = self.meth_return_graph_ticks()

        fig_prop_epi = (p9.ggplot(temp_df4, p9.aes(x="date_epi", y="percent"))
                        + p9.geom_bar(stat="identity",
                                      fill="darkcyan")
                        # + p9.theme_bw(base_size=20)
                        + p9.xlab("")
                        + p9.ylab("Percentage Signal/Total Seqs.")
                        + p9.scale_x_date(limits=limits,
                                          breaks=breaks.astype('str').tolist(),
                                          labels=labels.astype('str').tolist())
                        + p9.theme(axis_text_x=p9.element_text(angle=90),
                                   figure_size=(25, 5))
                        + p9.ggtitle(f"Weekly Proportional EPI-Curve: Prev. 7 Weeks -> Last Week \n"
                                     f"SIGNAL: {self.signal_no}, {self.lineage}, {self.mutations}")
                        + p9.stat_summary(p9.aes(label='stat(y)', group=1, ), fun_y=sum, geom="text", size=12)
                        + p9.facet_wrap("region_totals", nrow=1))

        p9.ggsave(plot=fig_prop_epi,
                  filename="fig_percentage_region_weekly_epi_curves.png",
                  path=self.path_save_dir)
        temp_df4.to_csv(self.path_save_dir + "/fig_percentage_region_weekly_epi_curves.csv")

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
        # print(temp_df_map["region_code"].value_counts())
        temp_df_map = temp_df_map.groupby("region_code").agg({"sample_id": pd.Series.nunique, "id": "max"})[
            ["sample_id", "id"]].reset_index()
        # print(temp_df_map)

        fig_map_totals = px.choropleth_mapbox(temp_df_map,
                                              locations="id",
                                              geojson=json_utla,
                                              color='sample_id',
                                              mapbox_style='white-bg',
                                              labels={"sample_id": "no. Seqs."})
        fig_map_totals.update_layout(mapbox_style="carto-positron",
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
        if self.data_region == "uk":
            val_loss_map_seqs = self.meth_generate_map_uk()
            return val_loss_map_seqs
        elif self.data_region == "int":
            self.meth_generate_map_int()
            return 0
