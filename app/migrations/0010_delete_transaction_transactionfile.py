from django.db import migrations


def delete_transaction_uploaded_files(apps, schema_editor):
    UploadedFile = apps.get_model('app', 'UploadedFile')
    UploadedFile.objects.filter(file_type='transaction').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_transactionfile_is_deleted'),
    ]

    operations = [
        migrations.RunPython(
            delete_transaction_uploaded_files,
            migrations.RunPython.noop,
        ),
        migrations.DeleteModel(name='Transaction'),
        migrations.DeleteModel(name='TransactionFile'),
    ]
