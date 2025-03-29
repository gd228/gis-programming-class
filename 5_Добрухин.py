from qgis.core import *

# Получаем слои
stations_layer = QgsProject.instance().mapLayersByName('stations')[0]
districts_layer = QgsProject.instance().mapLayersByName('districts')[0]

# Проверяем наличие необходимых полей в станциях
required_fields = ['some_value', 'depth']
for field in required_fields:
    if field not in stations_layer.fields().names():
        raise ValueError(f"В слое stations отсутствует обязательное поле: {field}")

# Создаем слой буферов
buffer_layer = QgsVectorLayer('Polygon?crs=EPSG:3857', 'buffers', 'memory')
buffer_provider = buffer_layer.dataProvider()
buffer_provider.addAttributes(stations_layer.fields())
buffer_layer.updateFields()

# Часть 1: Буферизация станций с depth > 50
buffer_features = []
for station in stations_layer.getFeatures():
    try:
        # Получаем значения с проверкой типов
        some_value = float(station['some_value'])
        depth = float(station['depth'])
        
        # Проверяем условие по глубине
        if depth > 50:
            radius = some_value * 30
            buffer_geom = station.geometry().buffer(radius, 8)
            
            new_feature = QgsFeature()
            new_feature.setGeometry(buffer_geom)
            new_feature.setAttributes(station.attributes())
            buffer_features.append(new_feature)
            
    except (ValueError, TypeError) as e:
        
        continue

# Добавляем буферы в слой
buffer_provider.addFeatures(buffer_features)
buffer_layer.updateExtents()
QgsProject.instance().addMapLayer(buffer_layer)

# Часть 2: Поиск пересечений с районами
selected_districts = []
for buffer_feature in buffer_layer.getFeatures():
    for district in districts_layer.getFeatures():
        if buffer_feature.geometry().intersects(district.geometry()):
            selected_districts.append(district.id())

# Выделяем районы
if selected_districts:
    districts_layer.select(selected_districts)
    print(f"Успешно! ")
