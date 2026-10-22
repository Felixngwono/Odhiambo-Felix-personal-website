from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('StoryTeller', '0006_alter_imagegallery_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='phone',
            field=models.CharField(max_length=20),
        ),
    ]
