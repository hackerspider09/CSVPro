# Generated by Django 5.1.6 on 2025-03-05 08:49

import core.models
import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ProcessData',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('csv_file', models.FileField(upload_to=core.models.getCsvIpPath, verbose_name='Csv Input')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('message', models.CharField(blank=True, max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProductData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('process_data', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.processdata')),
            ],
        ),
        migrations.CreateModel(
            name='ImageData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('input_url', models.URLField()),
                ('output_url', models.URLField(blank=True, null=True)),
                ('product_data', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.productdata')),
            ],
        ),
    ]
