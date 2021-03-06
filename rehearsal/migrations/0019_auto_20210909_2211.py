# Generated by Django 3.2.7 on 2021-09-09 13:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('production', '0009_auto_20210909_2211'),
        ('rehearsal', '0018_rehearsal_member'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='rehearsal',
            options={},
        ),
        migrations.RemoveField(
            model_name='rehearsal',
            name='end_time',
        ),
        migrations.RemoveField(
            model_name='rehearsal',
            name='start_time',
        ),
        migrations.AddField(
            model_name='rehearsal',
            name='prog',
            field=models.CharField(choices=[('0', ' '), ('2', 'DONE!!!'), ('1', 'half')], default='0', max_length=6),
        ),
        migrations.AlterField(
            model_name='rehearsal',
            name='date',
            field=models.DateField(verbose_name='DEADLINE'),
        ),
        migrations.AlterField(
            model_name='rehearsal',
            name='member',
            field=models.CharField(blank=True, max_length=15, verbose_name='STAFF'),
        ),
        migrations.AlterField(
            model_name='rehearsal',
            name='note',
            field=models.TextField(blank=True, verbose_name='TASK'),
        ),
        migrations.AlterField(
            model_name='rehearsal',
            name='production',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='production.production', verbose_name='PLOJECT'),
        ),
    ]
