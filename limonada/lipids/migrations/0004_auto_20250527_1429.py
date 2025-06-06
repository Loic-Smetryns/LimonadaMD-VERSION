# Generated by Django 2.2.28 on 2025-05-27 14:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lipids', '0003_auto_20250422_0929'),
    ]

    operations = [
        migrations.AddField(
            model_name='topology',
            name='root_version',
            field=models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.DO_NOTHING, to='lipids.Topology'),
        ),
        migrations.AddField(
            model_name='topology',
            name='t_version',
            field=models.IntegerField(default=1),
        ),
    ]
