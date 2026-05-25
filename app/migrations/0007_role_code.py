from django.db import migrations, models


def fill_default_codes(apps, schema_editor):
    Role = apps.get_model('app', 'Role')
    for role in Role.objects.all():
        role.code = f'ROLE_{role.id}'
        role.save(update_fields=['code'])


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_menu_parent_alter_menu_url_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='role',
            name='code',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.RunPython(fill_default_codes, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='role',
            name='code',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
