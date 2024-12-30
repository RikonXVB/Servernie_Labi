from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

# Корневой маршрут для проверки работы API
@app.route('/')
def home():
    data = {"message": "API работает"}
    return Response(
        json.dumps(data, ensure_ascii=False),
        mimetype='application/json; charset=utf-8'
    )

# Простая база данных в виде списка книг
books = [
    {"id": 1, "title": "Война и мир", "author": "Лев Толстой"},
    {"id": 2, "title": "Преступление и наказание", "author": "Фёдор Достоевский"}
]

# GET - получить все книги
@app.route('/books', methods=['GET'])
def get_books():
    return Response(
        json.dumps(books, ensure_ascii=False),
        mimetype='application/json; charset=utf-8'
    )

# GET - получить книгу по id
@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = next((book for book in books if book['id'] == book_id), None)
    if book is None:
        return Response(
            json.dumps({"error": "Книга не найдена"}, ensure_ascii=False),
            status=404,
            mimetype='application/json; charset=utf-8'
        )
    return Response(
        json.dumps(book, ensure_ascii=False),
        mimetype='application/json; charset=utf-8'
    )

# POST - добавить новую книгу
@app.route('/books', methods=['POST'])
def add_book():
    if not request.json or 'title' not in request.json or 'author' not in request.json:
        return Response(
            json.dumps({"error": "Необходимо указать название и автора"}, ensure_ascii=False),
            status=400,
            mimetype='application/json; charset=utf-8'
        )
    
    new_book = {
        'id': max(book['id'] for book in books) + 1,
        'title': request.json['title'],
        'author': request.json['author']
    }
    books.append(new_book)
    return Response(
        json.dumps(new_book, ensure_ascii=False),
        status=201,
        mimetype='application/json; charset=utf-8'
    )

# PUT - обновить существующую книгу
@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    book = next((book for book in books if book['id'] == book_id), None)
    if book is None:
        return Response(
            json.dumps({"error": "Книга не найдена"}, ensure_ascii=False),
            status=404,
            mimetype='application/json; charset=utf-8'
        )
    
    if not request.json:
        return Response(
            json.dumps({"error": "Нет данных для обновления"}, ensure_ascii=False),
            status=400,
            mimetype='application/json; charset=utf-8'
        )
    
    book['title'] = request.json.get('title', book['title'])
    book['author'] = request.json.get('author', book['author'])
    return Response(
        json.dumps(book, ensure_ascii=False),
        mimetype='application/json; charset=utf-8'
    )

# DELETE - удалить книгу
@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = next((book for book in books if book['id'] == book_id), None)
    if book is None:
        return Response(
            json.dumps({"error": "Книга не найдена"}, ensure_ascii=False),
            status=404,
            mimetype='application/json; charset=utf-8'
        )
    
    books.remove(book)
    return Response(
        json.dumps({"message": "Книга успешно удалена"}, ensure_ascii=False),
        mimetype='application/json; charset=utf-8'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)