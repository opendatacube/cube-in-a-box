import folium
from folium.plugins import Draw
from django.shortcuts import render
from django.http import JsonResponse

def map_view(request):
    # Crie um mapa base com a localização inicial
    m = folium.Map(location=[-19.917299, -43.934559], zoom_start=13)

    # Configurar as opções de desenho
    draw = Draw(
        draw_options={
            'polyline': False,
            'polygon': False,
            'circle': False,
            'circlemarker': False,
            'marker': False,
            'rectangle': True
        }
    )

    # Adicione o plugin de desenho ao mapa
    draw.add_to(m)

    # Representação HTML do mapa
    m = m._repr_html_()

    return render(request, 'maps/mapa.html', {'mapa': m})


def get_cube(request):
    if request.method == 'POST':
        latitude_inicial = request.POST.get('latitude_inicial')
        longitude_inicial = request.POST.get('longitude_inicial')
        latitude_final = request.POST.get('latitude_final')
        longitude_final = request.POST.get('longitude_final')

        # Aqui você adiciona a lógica para buscar o cubo de dados
        # Por exemplo, usando Open Data Cube ou outra biblioteca

        # Substitua isso pelo resultado real da sua busca
        resultado = {
            "status": "sucesso",
            "dados": "Dados do cubo aqui"
        }

        return JsonResponse(resultado)

    else:
        # Se não for um POST, redirecione ou mostre um erro
        return JsonResponse({"status": "erro", "mensagem": "Método não suportado"})
