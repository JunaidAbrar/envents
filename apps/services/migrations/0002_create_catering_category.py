from django.db import migrations

def create_catering_category(apps, schema_editor):
    ServiceCategory = apps.get_model('services', 'ServiceCategory')
    
    # Check if catering category already exists
    if not ServiceCategory.objects.filter(name='Catering').exists():
        # Create the category
        catering_category = ServiceCategory(
            name='Catering',
            slug='catering',
            description='Food and beverage services for events',
            icon='fa-utensils'
        )
        catering_category.save()

def remove_catering_category(apps, schema_editor):
    ServiceCategory = apps.get_model('services', 'ServiceCategory')
    ServiceCategory.objects.filter(name='Catering').delete()

class Migration(migrations.Migration):

    dependencies = [
        ('services', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_catering_category, remove_catering_category),
    ]