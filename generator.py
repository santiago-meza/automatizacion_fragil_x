from docxtpl import DocxTemplate


def generate_report(template, output_file, context):

    doc = DocxTemplate(template)

    doc.render(context)

    doc.save(output_file)