from django.db import migrations

def delete_additional_users(apps, schema_editor):
    User = apps.get_model('accounts', 'User')
    names_to_delete = [
        "Pedro Miguel",
        "Maria Luiza",
        "Gabriela Barros",
        "joao pedro",
        "Ana Sophia",
        "João Guilherme",
        "Ana Julia",
        "Luigi Casa",
        "Matheus Santos",
        "cicero silva",
        "Emily Sales",
        "Cecilia Lopes",
        "renyer martins",
        "Juan Teixeira"
    ]
    
    count = 0
    for name in names_to_delete:
        deleted, _ = User.objects.filter(nome_completo__iexact=name).delete()
        if deleted:
            count += deleted
            print(f"Deleted user(s) with name matching: {name}")

    print(f"Total additional users deleted: {count}")

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_delete_unwanted_users'),
    ]

    operations = [
        migrations.RunPython(delete_additional_users),
    ]
