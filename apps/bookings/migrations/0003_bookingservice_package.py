from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0002_servicepackage'),
        ('bookings', '0002_booking_phone_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookingservice',
            name='package',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='booking_services', to='services.servicepackage'),
        ),
    ]