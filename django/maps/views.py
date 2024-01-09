import folium
from folium.plugins import Draw
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse

import rasterio
from rasterio.io import MemoryFile
import io
import zipfile
import numpy as np

import datacube

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

        # request
        query = {
            'latitude': ( latitude_inicial, latitude_final),
            'longitude': ( longitude_inicial, longitude_final),
        }
        #remove hard coded
        product_name = 'aerial_image_1999'
        
        dc = datacube.Datacube()
        dc.index.products.get_by_name(product_name)

        product_info = dc.index.products.get_by_name(product_name)
        resolution = product_info.definition['storage']['resolution']
        crs = product_info.definition['storage']['crs']

        ds = dc.load(product=product_name, output_crs=crs, resolution=(resolution['x'],resolution['y']), **query)

        all_bands = ds.data_vars
        
        available_times = ds.time.values

        selected_data = ds.isel(time=0).to_array().transpose('y', 'x', 'variable')
        
        # Supondo que 'selected_data' é o seu xarray.DataArray
        data = selected_data.values

        # Removendo a primeira dimensão se for 1 (supondo formato (1, altura, largura, bandas))
        if data.ndim == 4:
            data = data.squeeze(0)

        num_bands = data.shape[-1]

        # Buffer para armazenar o arquivo ZIP
        zip_buffer = io.BytesIO()

        # Criar um arquivo ZIP em memória
        with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
            for i in range(num_bands):
                # Criar um TIFF para cada banda
                with MemoryFile() as memfile:
                    with memfile.open(
                        driver='GTiff',
                        height=data.shape[0],
                        width=data.shape[1],
                        count=1,
                        dtype=data.dtype,
                        crs=crs
                    ) as dataset:
                        dataset.write(data[:, :, i], 1)

                    # Adicionar o TIFF ao arquivo ZIP
                    memfile.seek(0)
                    zip_file.writestr(f'band_{i+1}.tif', memfile.read())

        # Preparar a resposta
        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="datacube_images.zip"'

        return response

    else:
        # Se não for um POST, redirecione ou mostre um erro
        return JsonResponse({"status": "error", "message": "Method not supported"})
