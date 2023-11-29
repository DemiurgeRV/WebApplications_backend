from django.shortcuts import render

data = {'data': {'filters': [
            {'name': 'Обрезка и поворот', 'id': 1, 'image_url': 'main/img/editor-img.png',
             'price': '25', 'time': '1-2'},
            {'name': 'Коррекция изображения', 'id': 2, 'image_url': 'main/img/preset-img.jpg',
             'price': '60', 'time': '1-2'},
            {'name': 'Фоторамки, стикеры и текст', 'id': 3, 'image_url': 'main/img/dog-img-3.jpg',
             'price': '35-50', 'time': '2'},
            {'name': 'Фотоэффекты и фотофильтры', 'id': 4, 'image_url': 'main/img/effects-img.jpg',
             'price': '100', 'time': '2'},
            {'name': 'Комплексная обработка', 'id': 5, 'image_url': 'main/img/photo-processing-img.png',
             'price': '600', 'time': '5'},
        ]
    }}

def getFilters(request):
    info = []
    input_text = request.GET.get('find')
    if input_text is not None:
        for filter in data['data']['filters']:
            if input_text in filter['name']:
                info.append(filter)
        return render(request, 'main/AllFilters.html', { 'data' : { 'filters' : info }})

    else:
        return render(request, 'main/AllFilters.html', data)

def getFilter(request, id):
    arrFilters = data['data']['filters']
    choice = {}
    for filter in arrFilters:
        if filter['id'] == id:
            choice = filter
    return render(request, 'main/OneFilter.html', choice)