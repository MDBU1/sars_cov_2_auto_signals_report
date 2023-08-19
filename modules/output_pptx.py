import os
import pandas as pd
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.util import Pt, Cm
from pptx.enum.shapes import MSO_SHAPE
from datetime import date
from pptx.dml.color import ColorFormat, RGBColor
from pd2ppt import df_to_table
from pptx.enum.text import PP_ALIGN
from pd2ppt import df_to_table

from modules.output_graphs import ClassOutputGraphs


# %%


class ClassPresentationSetup(ClassOutputGraphs):
    def __init__(self):
        super().__init__()
        self.str_prs_signal_call = self.meth_return_prs_name()
        self.meth_generate_slide_titles()
        self.meth_generate_slide_epi()
        self.meth_generate_slide_genetic()
        self.meth_generate_slide_overview()

    # Slide Components
    def meth_return_prs_name(self):
        temp_str_signal_call = f"SIGNAL: {self.signal_no} {self.lineage} {self.mutations}"
        return temp_str_signal_call

    def meth_slide_header(self, input_slide):
        slide1_header = input_slide.shapes.add_textbox(Cm(4), Cm(0), Cm(10), Cm(0.1))
        tf = slide1_header.text_frame
        p = tf.paragraphs[0]
        p.text = f"OFFICIAL REVIEW " + "{:%Y%m%d}".format(date.today()) + f" {self.meth_return_prs_name()}"
        p.font.size = Pt(10)
        p.font.name = 'Calibri'
        p.font.color.rgb = RGBColor(0, 124, 145)
        tf.paragraphs[0].alignment = PP_ALIGN.LEFT

    def meth_slide_footer(self, input_slide):
        slide1_footer = input_slide.shapes.add_textbox(Cm(4), Cm(18.25), Cm(10), Cm(0.1))
        tf = slide1_footer.text_frame
        p = tf.paragraphs[0]
        p.text = f"OFFICIAL REVIEW " + "{:%Y%m%d}".format(date.today()) + f" {self.meth_return_prs_name()}"
        p.font.size = Pt(10)
        p.font.name = 'Calibri'
        p.font.color.rgb = RGBColor(0, 124, 145)
        tf.paragraphs[0].alignment = PP_ALIGN.LEFT

    def meth_generate_slide(self):
        prs = Presentation(self.prs_slide_main)
        slide1_layout = prs.slide_layouts[0]
        slide1 = prs.slides.add_slide(slide1_layout)
        slide1 = prs.slides[0]
        self.meth_slide_header(slide1)
        self.meth_slide_footer(slide1)
        # self.meth_add_summary_box(slide1)
        del prs.slides._sldIdLst[1]
        return prs

    def meth_add_slide_title(self, input_slide, slide_name):
        slide1_title = input_slide.shapes.add_textbox(Cm(4.8), Cm(0.75), Cm(15), Cm(5))
        tf = slide1_title.text_frame
        p = tf.paragraphs[0]
        p.text = f"SARs-CoV-2 SIGNAL ANALYSIS: {self.data_region.upper()} {slide_name}"
        p.font.size = Pt(28)
        p.font.name = 'Calibri'
        p.font.color.rgb = RGBColor(0, 124, 145)
        tf.paragraphs[0].alignment = PP_ALIGN.LEFT
        return 0

    # Title Slide
    def meth_generate_slide_titles(self):
        prs = Presentation(self.prs_slide_title)

        slide1_layout = prs.slide_layouts[0]
        slide1 = prs.slides.add_slide(slide1_layout)

        slide1_title = slide1.shapes.add_textbox(Cm(8.5), Cm(7.5), Cm(15), Cm(7.5))
        tf = slide1_title.text_frame
        p = tf.paragraphs[0]
        p.text = "SARs-CoV-2 SIGNAL REVIEW"
        p.font.size = Pt(40)
        p.font.name = 'Calibri'
        p.font.color.rgb = RGBColor(0, 124, 145)
        tf.paragraphs[0].alignment = PP_ALIGN.LEFT

        sub = tf.add_paragraph()
        sub.text = self.str_prs_signal_call
        sub.font.size = Pt(34)
        sub.font.name = 'Calibri'
        sub.font.color.rgb = RGBColor(0, 124, 145)

        sub_date = tf.add_paragraph()
        sub_date.text = "\n" "{:%Y%m%d}".format(date.today())
        sub_date.font.size = Pt(14)
        sub_date.font.name = 'Calibri'
        sub_date.font.color.rgb = RGBColor(0, 124, 145)

        del prs.slides._sldIdLst[0]  # deletes base "template" slide
        prs.save(self.path_save_dir + "/" + "{:%Y%m%d}".format(date.today()) + "_SA_presentation_title_%s" %
                 self.str_prs_signal_call + ".pptx")
        return 0

    # Overview Slide
    def meth_add_signal_vs_top_lineages(self, input_slide):
        file = self.path_save_dir + "/fig_lineage_percentages.png"
        if not os.path.isfile(file):
            print("lineage percentages figure not found")
        else:
            left = Cm(1.5)
            top = Cm(2.5)
            width = Cm(15)
            height = Cm(9)
            pic = input_slide.shapes.add_picture(file, left, top, width, height)

    def meth_add_signal_weekly_cumulative_fig(self, input_slide):
        file = self.path_save_dir + "/fig_weekly_cumulative_epi.png"
        if not os.path.isfile(file):
            print("cumulative epi curve not found")
        else:
            left = Cm(17)
            top = Cm(2.5)
            width = Cm(15)
            height = Cm(9)
            pic = input_slide.shapes.add_picture(file, left, top, width, height)

    def meth_generate_slide_overview(self):
        prs = self.meth_generate_slide()
        slide = prs.slides[0]
        self.meth_add_signal_vs_top_lineages(slide)
        self.meth_add_signal_weekly_cumulative_fig(slide)
        self.meth_add_slide_title(slide, "Overview")
        prs.save(self.path_save_dir + "/" + "{:%Y%m%d}".format(date.today()) + "_SA_overview_" +
                 self.str_prs_signal_call + ".pptx")

    # EPI SLide
    def meth_add_epi_curve(self, input_slide):
        file = self.path_save_dir + "/fig_epi_curve.png"
        if not os.path.isfile(file):
            print("epi. curve not found")
        else:
            left = Cm(1.5)
            top = Cm(1)
            width = Cm(25)
            height = Cm(9)
            pic = input_slide.shapes.add_picture(file, left, top, width, height)

    def meth_add_prop_epi_curve(self, input_slide):
        file_prop_region_epi_curve = self.path_save_dir + "/fig_percentage_region_weekly_epi_curves.png"
        if not os.path.isfile(file_prop_region_epi_curve):
            print("prop. epi. curves not found")
        else:
            left = Cm(1.5)
            top = Cm(9.25)
            width = Cm(22)
            height = Cm(9)
            pic = input_slide.shapes.add_picture(file_prop_region_epi_curve, left, top, width, height)

    def meth_add_map_int(self, input_slide, input_file):
        #file = self.path_save_dir + "/fig_int_map.png"
        file = input_file
        if not os.path.isfile(file):
            print("int map not found")
        else:
            left = Cm(23.35)
            top = Cm(9.25)
            width = Cm(10.5)
            height = Cm(9)
            pic = input_slide.shapes.add_picture(file, left, top, width, height)

    def meth_add_epi_slide_summary_box(self, input_slide):
        # summary text
        rect0 = input_slide.shapes.add_shape(  # Add Shape object➀
            MSO_SHAPE.RECTANGLE,  # Specify the shape type as "Rounded Rectangle"
            Cm(26.5), Cm(1.25),  # Insertion position is specified as the upper left coordinate of the shape
            Cm(7.2), Cm(8.25))  # Specify the width and height of the inserted shape
        fill = rect0.fill
        fill.solid()
        fill.fore_color.rgb = RGBColor(255, 255, 255)
        line = rect0.line
        line.color.rgb = RGBColor(0, 124, 145)
        # self.func_summary_epi_text(rect0)
        return rect0

    def meth_generate_slide_epi(self):
        prs = self.meth_generate_slide()
        slide = prs.slides[0]
        if self.data_region == "uk":
            file = self.path_save_dir + "/map_UTLA_counts.png"
            self.meth_add_map_int(slide, file)
        elif self.data_region == "int":
            file = self.path_save_dir + "/fig_int_map.png"
            self.meth_add_map_int(slide, file)
        self.meth_add_epi_curve(slide)
        self.meth_add_prop_epi_curve(slide)
        self.meth_add_slide_title(slide, "EPI")
        rect = self.meth_add_epi_slide_summary_box(slide)
        prs.save(self.path_save_dir + "/" + "{:%Y%m%d}".format(date.today()) + "_SA_presentation_epi_" +
                 self.str_prs_signal_call + ".pptx")

    # Genetic SLide

    def meth_add_mutation_profile_table(self, input_slide):
        left = Cm(1.5)
        top = Cm(2.25)
        width = Cm(30)
        height = Cm(9)
        table = df_to_table(input_slide, self.df_profile_mutation_ordered, left, top, width, height)
        for shape in input_slide.shapes:
            if shape.has_table:
                table = shape.table
                table.columns[0].width = Cm(2)
                table.columns[1].width = Cm(30)

                def iter_cells(table):
                    for row in table.rows:
                        for cell in row.cells:
                            yield cell

                for cell in iter_cells(table):
                    for paragraph in cell.text_frame.paragraphs:
                        for run in paragraph.runs:
                            run.font.size = Pt(12)


    def meth_add_genetics_slide_summary_box(self, input_slide):
        rect0 = input_slide.shapes.add_shape(  # Add Shape object➀
            MSO_SHAPE.RECTANGLE,  # Specify the shape type as "Rounded Rectangle"
            Cm(1.5), Cm(16),  # Insertion position is specified as the upper left coordinate of the shape
            Cm(32), Cm(2))  # Specify the width and height of the inserted shape
        fill = rect0.fill
        fill.solid()
        fill.fore_color.rgb = RGBColor(255, 255, 255)
        line = rect0.line
        line.color.rgb = RGBColor(0, 124, 145)
        # self.func_summary_epi_text(rect0)
        return rect0

    def meth_return_genetics_slide_summary_text(self, insert_text_box):
        insert_text_box.text = ("Unique mutation/s compared with parent lineage: "
                                + "\n" +
                                "Unique mutation/s compared with top ten circulating lineages: "
                                + "\n" +
                                "Mutations conserved in <=0.5 top circulating lineages: "
                                + "\n" +
                                "Note. Mutations conserved based within analysis time-period.")

        for x in range(len(insert_text_box.text_frame.paragraphs)):
            p = insert_text_box.text_frame.paragraphs[x]
            p.font.size = Pt(10)
            p.font.name = 'Arial'
            p.font.color.rgb = RGBColor(0, 0, 0)

    def meth_generate_slide_genetic(self):
        prs = self.meth_generate_slide()
        slide = prs.slides[0]
        self.meth_add_mutation_profile_table(slide)
        rect = self.meth_add_genetics_slide_summary_box(slide)
        self.meth_return_genetics_slide_summary_text(rect)
        self.meth_add_slide_title(slide, "Genetics")
        prs.save(self.path_save_dir + "/" + "{:%Y%m%d}".format(date.today()) + "_SA_presentation_genetic_" +
                 self.str_prs_signal_call + ".pptx")


