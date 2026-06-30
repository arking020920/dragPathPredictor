@api_bp.route('/drog', methods=['POST'])
# @jwt_required()  # Descomenta si necesitas autenticación
def drog_route():
    # Obtener los datos del frontend
    data_front = request.get_json()
    print("Datos recibidos del frontend:", data_front)  # Muestra los datos recibidos en la consola

    # Procesar los datos con la función 'drog'
    kml_content = drog(data_front)
    print("Contenido del KML después de procesar:", kml_content)  # Muestra el KML generado en la consola

    # Preparar la respuesta a enviar al frontend
    response = jsonify({'kml_content': kml_content})
    print("Respuesta enviada al frontend:", response.json)  # Muestra la respuesta en la consola

    # Devolver la respuesta JSON al cliente
    return response
