from django.shortcuts import render

def getFilters(request):
    return render(request, 'main/AllFilters.html', {'data': {
        'filters': [
            {'name': 'Обрезка и поворот', 'id': 1, 'image_url': 'main/img/editor-img.png', 'price': '25', 'time': '1-2'},
            {'name': 'Коррекция изображения', 'id': 2, 'image_url': 'main/img/preset-img.jpg', 'price': '60', 'time': '1-2'},
            {'name': 'Фоторамки, стикеры и текст', 'id': 3, 'image_url': 'main/img/dog-img-1.jpg', 'price': '35-50', 'time': '2'},
            {'name': 'Услуга 4', 'id': 4, 'image_url': 'main/img/editor-img.png', 'price': '', 'time': ''},
        ]
    }})

def getFilter(request, id):
    return render(request, 'main/OneFilter.html', {'data': {
        'id': id
    }})