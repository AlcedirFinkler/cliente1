# models.py from app monitorESP

from django.db import models
import uuid

class ESP32Device(models.Model):
    registration_number = models.UUIDField(default=uuid.uuid4, unique=True)
    equipamento = models.ForeignKey(
        'CadEquip.Equipamento',
        on_delete=models.CASCADE,
        related_name='esp_devices',
        null=True,
        blank=True
    )
    horimetro = models.FloatField(null=True, blank=True)
    horimetro_offset = models.FloatField(default=0)
    atualizacao_automatica = models.BooleanField(default=False)
    last_update = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.equipamento.nome if self.equipamento else 'Sem equipamento'} ({self.registration_number})"