
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Airplane',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('model', models.CharField(max_length=100)),
                ('capacity', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Airport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('city', models.CharField(max_length=100)),
                ('code', models.CharField(max_length=10, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Passenger',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('email', models.EmailField(max_length=254, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Flight',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('flight_number', models.CharField(max_length=20, unique=True)),
                ('departure_time', models.DateTimeField()),
                ('arrival_time', models.DateTimeField()),
                ('airplane', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='flights', to='main.airplane')),
                ('arrival_airport', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='arriving_flights', to='main.airport')),
                ('departure_airport', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='departing_flights', to='main.airport')),
            ],
            options={
                'ordering': ['departure_time'],
            },
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('seat_number', models.CharField(max_length=10)),
                ('booking_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('flight', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to='main.flight')),
                ('passenger', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to='main.passenger')),
            ],
            options={
                'ordering': ['-booking_date'],
                'constraints': [models.UniqueConstraint(fields=('flight', 'seat_number'), name='unique_seat_per_flight')],
            },
        ),
    ]
