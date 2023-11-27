from django.shortcuts import render

def getFilters(request):
    return render(request, 'main/AllFilters.html', {'data': {
        'filters': [
            {'name': 'Обрезка и поворот', 'id': 1, 'image_url': 'main/img/editor-img.png', 'price': '25', 'time': '1-2'},
            {'name': 'Коррекция изображения', 'id': 2, 'image_url': 'main/img/preset-img.jpg', 'price': '60', 'time': '1-2'},
            {'name': 'Фоторамки, стикеры и текст', 'id': 3, 'image_url': 'main/img/dog-img-3.jpg', 'price': '35-50', 'time': '2'},
            {'name': 'Фотоэффекты и фотофильтры', 'id': 4, 'image_url': 'main/img/effects-img.jpg', 'price': '100', 'time': '2'},
            {'name': 'Комплексная обработка', 'id': 5, 'image_url': 'main/img/photo-proccesing-img.png', 'price': '600', 'time': '5'},
        ]
    }})

def getFilter(request, id):
    return render(request, 'main/OneFilter.html', {'data': {
        'id': id
    }})