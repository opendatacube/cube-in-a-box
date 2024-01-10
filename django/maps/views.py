import folium
from folium.plugins import Draw
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import json
from rasterio.io import MemoryFile
import io
import zipfile
import base64
import matplotlib.pyplot as plt


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


def download_cube(request):
    if request.method == 'POST':
        query = process_request(request)
        data, crs = load_datacube_data(query)
        zip_buffer = create_zip(data, crs)
        return generate_http_response(zip_buffer)
    else:
        return JsonResponse({"status": "error", "message": "Method not supported"})
    

def get_images(request):
    if request.method == 'POST':
        query = process_request(request)
        data, _ = load_datacube_data(query)
        print("************")
        print(query)

        images_base64 = []
        for i in range(data.shape[-1]):
            img = data[:, :, i]  # Pegue a imagem do canal i
            buffered = io.BytesIO()
            plt.imsave(buffered, img, format="png")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            images_base64.append(f"data:image/png;base64,{img_str}")

        return JsonResponse({'images': images_base64})
    else:
        return JsonResponse({"status": "error", "message": "Method not supported"})
    

# Utils

def process_request(request):
    data = json.loads(request.body)
    latitude_inicial = data.get('latitude_inicial')
    longitude_inicial = data.get('longitude_inicial')
    latitude_final = data.get('latitude_final')
    longitude_final = data.get('longitude_final')

    if None in [latitude_inicial, longitude_inicial, latitude_final, longitude_final]:
        raise ValueError("Todos os valores de coordenadas devem ser fornecidos")

    return {
        'latitude': (float(latitude_inicial), float(latitude_final)),
        'longitude': (float(longitude_inicial), float(longitude_final)),
    }

def load_datacube_data(query):
    product_name = 'aerial_image_1999'
    dc = datacube.Datacube()
    product_info = dc.index.products.get_by_name(product_name)
    resolution = product_info.definition['storage']['resolution']
    crs = product_info.definition['storage']['crs']

    ds = dc.load(product=product_name, output_crs=crs, resolution=(resolution['x'], resolution['y']), **query)
    selected_data = ds.isel(time=0).to_array().transpose('y', 'x', 'variable')
    data = selected_data.values
    if data.ndim == 4:
        data = data.squeeze(0)
    data = data[::-1, ::-1, :]  #flip x and y axis

    return data, crs

def create_zip(data, crs):
    zip_buffer = io.BytesIO()
    num_bands = data.shape[-1]

    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
        for i in range(num_bands):
            with MemoryFile() as memfile:
                with memfile.open(driver='GTiff', height=data.shape[0], width=data.shape[1], count=1, dtype=data.dtype, crs=crs) as dataset:
                    dataset.write(data[:, :, i], 1)
                memfile.seek(0)
                zip_file.writestr(f'band_{i+1}.tif', memfile.read())

    return zip_buffer

def generate_http_response(zip_buffer):
    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="datacube_images.zip"'
    return response