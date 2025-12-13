from django.db import migrations
from django.db.models import Q

def delete_users(apps, schema_editor):
    User = apps.get_model('accounts', 'User')
    names_to_delete = [
        "Mariane garcia",
        "Emily sales",
        "Kaique jesus",
        "Oliver Andrade",
        "Ana sophia",
        "Luan pires",
        "Lorena Aparecida",
        "Cecília Lopes",
        "maria",
        "Maria Luiza",
        "Gabriela Peixoto",
        "marcos vinícius",
        "Felipe Sousa",
        "Luigi Casa",
        "vilena santana",
        "Fernando Camargo",
        "joao pedro",
        "Ágatha Martins",
        "Apollo Correia",
        "renyer martins",
        "Gabriel Barros",
        "Aylla Correia",
        "Pietra Moraes",
        "Lorena Cassiano",
        "Guilherme Novais",
        "Rodrigo Oliveira",
        "Juan Texeira",
        "abner lima",
        "cicero silva",
        "thiagotres",
        "Ana Julia",
        "Heloísa Andrade",
        "Pedro Miguel",
        "João Guilherme",
        "Isaque Cirino",
        "Isadora da cunha",
        "thiagodois",
        "Joana Silva",
        "Maria da Mata"
    ]
    
    # Iterate and delete case-insensitively
    count = 0
    for name in names_to_delete:
        # Using filter().delete() handles multiple matches (e.g. duplicate names)
        deleted, _ = User.objects.filter(nome_completo__iexact=name).delete()
        if deleted:
            count += deleted
            print(f"Deleted user(s) with name matching: {name}")

    print(f"Total users deleted: {count}")

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_alter_user_cpf'),
    ]

    operations = [
        migrations.RunPython(delete_users),
    ]
