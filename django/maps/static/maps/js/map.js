var map = L.map('map').setView([-19.917299, -43.934559], 13);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
}).addTo(map);

var drawnRectangle;
var drawnItems = new L.FeatureGroup();
map.addLayer(drawnItems);

var drawControl = new L.Control.Draw({
    edit: {
        featureGroup: drawnItems,
    },
    draw: {
        polygon: false,
        circle: false,
        circlemarker: false,
        marker: false,
        polyline: false,
        rectangle: {
            shapeOptions: {
                clickable: true,
            },
        },
    },
});

map.addControl(drawControl);

map.on('draw:created', function (e) {
    if (drawnRectangle) {
        map.removeLayer(drawnRectangle);
    }
    drawnRectangle = e.layer;
    map.addLayer(drawnRectangle);

    // Obter as coordenadas do retângulo
    var bounds = drawnRectangle.getBounds();
    var northEast = bounds.getNorthEast();
    var southWest = bounds.getSouthWest();

    // Preencher o formulário com as coordenadas
    document.getElementById('latitude_inicial').value = southWest.lat;
    document.getElementById('longitude_inicial').value = southWest.lng;
    document.getElementById('latitude_final').value = northEast.lat;
    document.getElementById('longitude_final').value = northEast.lng;

    drawnItems.addLayer(drawnRectangle);
});

map.on('click', function () {
    if (drawnRectangle) {
        map.removeLayer(drawnRectangle);
        drawnRectangle = null;

        document.getElementById('latitude_inicial').value = '';
        document.getElementById('longitude_inicial').value = '';
        document.getElementById('latitude_final').value = '';
        document.getElementById('longitude_final').value = '';
    }
});
