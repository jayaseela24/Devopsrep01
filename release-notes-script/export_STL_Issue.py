from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer,ListFlowable, ListItem
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import json
from reportlab.lib.pagesizes import letter

class JsonToPdfConverter:
    def load_json(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as e:
            print(e)
            return None

    def convert_to_pdf(self, json_data, pdf_filename):
        # Create a PDF document
        pdf = SimpleDocTemplate(pdf_filename, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        # Custom style for H1 heading
        h1 = ParagraphStyle('H1Style',parent=styles['Normal'], fontSize=18,spaceAfter=6, spaceBefore=6)
        heading = ("Example	PDF	– Communication – v2")

        elements.append(Paragraph(heading,h1))
        top_margin_height = 40
        elements.append(Spacer(1, top_margin_height))

        h3_style = ParagraphStyle('H3Style', parent=styles['Normal'], fontSize=14, spaceAfter=6, spaceBefore=6)

        intro_text = ("We wanted to provide	you	with an update on the recent deployment	and	address	some"	
                    "outstanding issues.Below is a summary of the completed	tasks and ongoing challenges "
                    "we are actively working to resolve.")
        elements.append(Paragraph(intro_text, styles['Normal']))

        top_margin_height = 20  # Height of the spacer in points, adjust as needed
        elements.append(Spacer(1, top_margin_height))

        completed_tasks = ("Completed Tasks:")
        elements.append(Paragraph(completed_tasks, h3_style))
        completed_tasks_style = ParagraphStyle('CompletedTasks', parent=styles['Normal'], leftIndent=20)
        completed_tasks_description = ("1. Deployment: The deployment process has been successfully completed, "
                           "and updated forms and RTL. Lawrence have been reloaded<br/><br/>"
                           "2. W-3 Testing:  We have passed the W-3 testing phase, and the updated form "
                           "will soon be available in staging for Terry to test.<br/>")

        elements.append(Paragraph(completed_tasks_description, completed_tasks_style))

        elements.append(Paragraph("<br/><br/>", styles['Normal']))

        resolved_issue = ("Issues Resolved: <br/>")
        elements.append(Paragraph(resolved_issue, h3_style))

        top_margin_height = 10  # Height of the spacer in points, adjust as needed
        elements.append(Spacer(1, top_margin_height))

        # Loop through each record in JSON data
        description_style = ParagraphStyle('DescriptionStyle', parent=styles['Normal'], wordWrap='WORD')
        issue_style = ParagraphStyle('BoldStyle', parent=styles['Normal'], fontName='Helvetica-Bold')
        table_data = []
        col_widths = [1 * inch, 5 * inch]
        for record in json_data:
            # Format the issue and description
            issue = record.get('issue', 'No Issue Number')
            description = record.get('description', 'No Description')
            description_para = Paragraph(description, description_style)
            formatted_issue = Paragraph(issue, issue_style)
            table_data.append([formatted_issue, description_para])

        if not table_data:
            elements.append(Paragraph("No linked issues found.", styles['Normal']))
        else:
            table_style = TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ])

            # Create the table
            issue_table = Table(table_data,colWidths=col_widths, style=table_style)
            table_indent = 5
            issue_table.hAlign = 'LEFT'
            issue_table.spaceBefore = table_indent

            elements.append(issue_table)

        top_margin_height = 20  # Height of the spacer in points, adjust as needed
        elements.append(Spacer(1, top_margin_height))

        Additional_Notes = ("Additional Notes:")
        elements.append(Paragraph(Additional_Notes, h3_style))


        bullet_points = [
            " An error in viewing conversion data in the staging environment may be	due to lack of updates, and	Jean is currently unavailable for clarification. Terry has confirmed that it is	working	in MO.",
            "Work is ongoing to resolve issues related to populating demographics in the payment coupon."
        ]

        bullet_list = ListFlowable(
            [ListItem(Paragraph(bp,styles['Normal']),leftIndent=30) for bp in bullet_points],
            bulletType='bullet',
            leftIndent=15,
        )

        elements.append(bullet_list)


        top_margin_height = 20  # Height of the spacer in points, adjust as needed
        elements.append(Spacer(1, top_margin_height))

        conclusion_text = "We appreciate your patience as we work to resolve these issues promptly. If you have any questions or require	further	clarification, please feel free to reach out."
        elements.append(Paragraph(conclusion_text,styles['Normal']))

        top_margin_height = 20  # Height of the spacer in points, adjust as needed
        elements.append(Spacer(1, top_margin_height))
        regard_text = "Best	Regards,"
        elements.append(Paragraph(regard_text,styles['Normal']))

        top_margin_height = 10  # Height of the spacer in points, adjust as needed
        elements.append(Spacer(1, top_margin_height))

        company_name ="<b>RSI</b>"
        elements.append(Paragraph(company_name,styles['Normal']))
        # Build the PDF
        pdf.build(elements)
        print("PDF generated successfully.")


converter = JsonToPdfConverter()
json_data = converter.load_json("STL_issue.json")  # Replace with the path to your JSON file

converter.convert_to_pdf(json_data, "STL_issues.pdf")
