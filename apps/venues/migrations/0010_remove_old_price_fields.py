# Manual migration to remove old price and price_type fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('venues', '0009_add_dynamic_pricing'),
    ]

    operations = [
        # Remove old price field if it exists
        migrations.RunSQL(
            sql='ALTER TABLE venues_venue DROP COLUMN IF EXISTS price;',
            reverse_sql='ALTER TABLE venues_venue ADD COLUMN IF NOT EXISTS price DECIMAL(10, 2);',
        ),
        # Remove old price_type field if it exists
        migrations.RunSQL(
            sql='ALTER TABLE venues_venue DROP COLUMN IF EXISTS price_type;',
            reverse_sql='ALTER TABLE venues_venue ADD COLUMN IF NOT EXISTS price_type VARCHAR(50);',
        ),
    ]
