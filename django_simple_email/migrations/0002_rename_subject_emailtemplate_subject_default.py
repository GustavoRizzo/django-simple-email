from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("django_simple_email", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="emailtemplate",
            old_name="subject",
            new_name="subject_default",
        ),
    ]
