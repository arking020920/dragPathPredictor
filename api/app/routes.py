from flask import Blueprint, jsonify, request, render_template
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from logica.drog.drog import drog

api_bp = Blueprint('api', __name__)#, static_folder='../front/assets', template_folder='../front'

@api_bp.route('/', methods=['GET'])
def home_route():
    return render_template('index.html')
    #return jsonify({'message': 'API is running'})


# Datos de usuarios de ejemplo
users = {
    "testuser": "password123"
}


#! <<<-------------------------LOGIN------------------------->>>
@api_bp.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    if username in users and users[username] == password:
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token)
    return jsonify({"msg": "Bad username or password"}), 401


@api_bp.route('/drog', methods=['POST'])
def drog_route():
    data_front = request.get_json()
    print(data_front)

    # Si es una lista de elementos, procesar cada uno secuencialmente
    if isinstance(data_front, list):
        kml_results = []

        for item in data_front:
            
                result = drog(item)
                print('ooaoaoaoa', result)
                kml_results.append(result)
            #except Exception as e:
             #   print('no llega nada papu aaaa')
              #  kml_results.append({'error': str(e)})

        return jsonify({'kml_content': kml_results})

    # Si es un solo objeto, procesar directamente
    else:
        try:
            kml_content = drog(data_front)
            return jsonify({'kml_content': kml_content})
        except Exception as e:
            return jsonify({'error': str(e)}), 500



'''
#! <<<-------------------------DROG------------------------->>>
@api_bp.route('/drog', methods=['POST'])
#@jwt_required()
def drog_route():
    
    data_front = request.get_json()
    print(data_front)
    
    kml_content = drog(data_front)
    
    #aqui van comillas
    from fastkml import kml

    # Crear un objeto KML
    k = kml.KML()

    # Abrir el archivo KML y cargarlo
    with open('aa/alltrack.kml', "rt", encoding="utf-8") as f:
        doc = f.read()
        
        kml_content = doc
    #aqui van comillas
    
    # Devolver el contenido del archivo KML como una respuesta JSON
    return jsonify({'kml_content': kml_content})
'''

#! <<<-------------------------CONTACT------------------------->>>
@api_bp.route('/contact', methods=['POST'])
def contact_route():
    
    data_contact = request.get_json()
    print(data_contact)
    
    return jsonify({"msg": "Send messenger succefull"})
