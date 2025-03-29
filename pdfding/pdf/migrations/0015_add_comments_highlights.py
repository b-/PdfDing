import uuid

import django.db.models.deletion
from django.db import migrations, models
from pdf.service import PdfProcessingServices


def set_highlights_and_comments(apps, schema_editor):
    """Set highlights and comments for all pdfs."""

    # for pdf in Pdf.objects.all():
    pdf_model = apps.get_model('pdf', 'Pdf')
    highlight_model = apps.get_model('pdf', 'PdfHighlight')
    comment_model = apps.get_model('pdf', 'PdfComment')

    for pdf in pdf_model.objects.all():
        PdfProcessingServices.set_highlights_and_comments(
            pdf, pdf_highlight_class=highlight_model, pdf_comment_class=comment_model
        )


def reverse_func(apps, schema_editor):  # pragma: no cover
    pass


class Migration(migrations.Migration):

    dependencies = [('pdf', '0014_add_pdf_revision'), ('users', '0017_add_annotation_sorting')]

    operations = [
        migrations.CreateModel(
            name='PdfComment',
            fields=[
                ('creation_date', models.DateTimeField(editable=False, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('page', models.IntegerField(null=True)),
                ('text', models.TextField(null=True)),
                ('pdf', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pdf.pdf')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PdfHighlight',
            fields=[
                ('creation_date', models.DateTimeField(editable=False, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('page', models.IntegerField(null=True)),
                ('text', models.TextField(null=True)),
                ('pdf', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pdf.pdf')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RunPython(set_highlights_and_comments, reverse_func),
    ]
