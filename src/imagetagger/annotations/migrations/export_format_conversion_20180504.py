from django.db import migrations


def convert_export_formats(apps, schema_editor):
    ExportFormat = apps.get_model('annotations', 'ExportFormat')
    conv_placeholders = {
        '%%x1': '%%minx',
        '%%relx1': '%%relminx',
        '%%x2': '%%maxx',
        '%%relx2': '%%relmaxx',
        '%%y1': '%%miny',
        '%%rely1': '%%relminy',
        '%%y2': '%%maxy',
        '%%rely2': '%%relmaxy',
    }
    for export_format in ExportFormat.objects.all():
        for key, value in conv_placeholders.items():
            export_format.annotation_format = export_format.annotation_format\
                .replace(key, str(value))
            export_format.save()


class Migration(migrations.Migration):

    dependencies = [
        ('annotations', '0024_auto_20180429_0005'),
    ]

    operations = [
        migrations.RunPython(convert_export_formats),
    ]
