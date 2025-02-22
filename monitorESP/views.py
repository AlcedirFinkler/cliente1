# views.py from app monitorESP

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import ESP32Device
from CadEquip.models import Equipamento
from django.contrib.auth.decorators import login_required

@login_required
def device_list(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))  # Garantir decodificação correta
            equipamento_id = data.get('equipamento_id')

            if not equipamento_id:
                return JsonResponse({'status': 'error', 'message': 'ID do equipamento não fornecido'})

            # Verifica se já existe um dispositivo para esse equipamento
            if ESP32Device.objects.filter(equipamento_id=equipamento_id).exists():
                return JsonResponse({'status': 'error', 'message': 'Já existe um dispositivo para este equipamento.'})

            equipamento = Equipamento.objects.get(id=equipamento_id)
            device = ESP32Device.objects.create(equipamento=equipamento)

            return JsonResponse({
                'status': 'success',
                'device': {
                    'id': device.id,
                    'registration_number': str(device.registration_number),
                    'equipamento_nome': device.equipamento.nome,
                    'equipamento_tag': device.equipamento.tag
                }
            })
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Erro ao decodificar JSON'})
        except Equipamento.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Equipamento não encontrado'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    devices = ESP32Device.objects.all().select_related('equipamento')
    equipamentos = Equipamento.objects.exclude(id__in=ESP32Device.objects.values_list('equipamento_id', flat=True))

    return render(request, 'device_list.html', {
        'devices': devices,
        'equipamentos': equipamentos
    })

@login_required
def toggle_auto_update(request, device_id):
    try:
        device = ESP32Device.objects.get(id=device_id)
        device.atualizacao_automatica = not device.atualizacao_automatica
        device.save()
        return JsonResponse({
            'status': 'success',
            'atualizacao_automatica': device.atualizacao_automatica
        })
    except ESP32Device.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Dispositivo não encontrado'})

@login_required
def update_offset(request, device_id):
    try:
        data = json.loads(request.body)
        new_offset = float(data.get('offset', 0))
        device = ESP32Device.objects.get(id=device_id)
        device.horimetro_offset = new_offset
        device.save()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@csrf_exempt
def atualiza_horimetro(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            registration_number = data.get('registration_number')
            horimetro = float(data.get('horimetro'))
            
            device = ESP32Device.objects.get(registration_number=registration_number)
            device.horimetro = round(horimetro, 1)
            device.save()
            
            if device.atualizacao_automatica and device.equipamento:
                valor_ajustado = horimetro + device.horimetro_offset
                device.equipamento.horimetro_atual = round(valor_ajustado, 1)
                device.equipamento.save()
            
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def update_horimetro_atual(request, device_id):
    try:
        data = json.loads(request.body)
        new_horimetro_atual = float(data.get('horimetro_atual', 0))
        device = ESP32Device.objects.get(id=device_id)
        
        if device.atualizacao_automatica:
            return JsonResponse({'status': 'error', 'message': 'Desative a atualização automática para alterar manualmente.'})
        
        device.equipamento.horimetro_atual = round(new_horimetro_atual, 1)
        device.equipamento.save()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
def delete_device(request, device_id):
    device = ESP32Device.objects.get(id=device_id)
    device.delete()
    return redirect('device_list')