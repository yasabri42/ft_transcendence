# Generated by Django 5.1.1 on 2024-09-30 00:07

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MapSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nbPlayer', models.CharField(default=2, help_text='number of users', max_length=3)),
                ('listOfPlayer', models.CharField(default='', help_text='list of player in json and if they are ready in json')),
                ('duringTime', models.CharField(default=0, help_text='time of the party')),
                ('date', models.DateField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Shape',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('party_id', models.CharField(default=-1, help_text='id of the party', max_length=7)),
                ('item_id', models.CharField(default=-1, help_text='id of the item', max_length=7)),
                ('type', models.CharField(choices=[('1', 'Border'), ('2', 'User'), ('3', 'Ball')], max_length=1)),
                ('color', models.CharField(help_text='hex', max_length=7)),
                ('posx', models.CharField(default=0, help_text='float position', max_length=7)),
                ('posy', models.CharField(default=0, help_text='float position', max_length=7)),
            ],
        ),
    ]