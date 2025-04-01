
import os
import logging
from flask import Flask, request, abort, jsonify, render_template, url_for, redirect, flash
import requests
from datetime import datetime
import json
from werkzeug.utils import secure_filename
from utils.monday_api import get_monday_data, update_monday_item
from utils.date_formatter import formatar_data, convert_date_to_monday_format

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize the Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key_for_development")

# Configure API key from environment variables
API_KEY = os.environ.get("MONDAY_API_KEY", "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjQxMDM1MDMyNiwiYWFpIjoxMSwidWlkIjo1NTIyMDQ0LCJpYWQiOiIyMDI0LTA5LTEzVDExOjUyOjQzLjAwMFoiLCJwZXIiOiJtZTp3cml0ZSIsImFjdGlkIjozNzk1MywicmduIjoidXNlMSJ9.hwTlwMwtbhKdZsYcGT7UoENBLZUAxnfUXchj5RZJBz4")
API_URL = "https://api.monday.com/v2"
MONDAY_BOARD_ID = 7307869243

# Configure file upload settings
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'csv', 'png', 'jpg', 'jpeg'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

# Define a filter for the Jinja2 template engine
def replace_none(valor):
    if valor is None or valor == "None" or valor == "" or valor == '""':
        return ''
    return valor

app.jinja_env.filters['replace_none'] = replace_none

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET'])
def home():
    logger.info("Home page accessed")
    return redirect(url_for('readequacao'))

@app.route('/readequacao', methods=['GET', 'POST'])
def readequacao():
    result = None

    if request.method == 'POST':
        
        num_negocio = request.form.get('negocio')
        logger.info(f"Searching for business number: {num_negocio}")

        if not num_negocio:
            flash("Por favor, insira um número de negócio", "danger")
            return render_template('readequacao.html')

        query = """
        query {
          items_page_by_column_values(
            limit: 50,
            board_id: %d,
            columns: [{ column_id: "texto__1", column_values: ["%s"] }]
          ) {
            items {
              id
              name
              column_values {
                id
                text
                value
              }
            }
          }
        }
        """ % (MONDAY_BOARD_ID, num_negocio)

        try:
            monday_response = get_monday_data(query, API_KEY, API_URL)
            items = monday_response.get('data', {}).get('items_page_by_column_values', {}).get('items', [])

            if items:
                item = items[0]
                name = item.get('name')
                item_id = item.get('id')

                # Define the columns we want to retrieve
                column_ids = [
                    "texto0__1", "lista_suspensa3__1", "data__1", "date3__1", 
                    "date9__1", "date7__1", "texto16__1", "dup__of_op__o_1c0__1", 
                    "dup__of_op__o_2c__1", "dup__of_op__o_3c9__1",
                    "dup__of_op__o_1a__1", "text0__1", "dup__of_op__o_1c5__1",
                    "dup__of_op__o_1c__1", "dup__of_op__o_3a__1", "dup__of_op__o_3b__1",
                    "dup__of_op__o_3c4__1", "dup__of_op__o_3c__1"
                ]
                column_values = {col_id: None for col_id in column_ids}

                # Extract column values from the item
                for column in item.get('column_values', []):
                    if column['id'] in column_ids:
                        column_values[column['id']] = column.get('text') or column.get('value')

                # Create result dictionary with column values
                result = {
                    "item_id": item_id,
                    "name": name,
                    "texto0__1": column_values.get('texto0__1'),
                    "lista_suspensa3__1": column_values.get('lista_suspensa3__1'),
                    "data__1": column_values.get('data__1'),
                    "date3__1": column_values.get('date3__1'),
                    "date9__1": column_values.get('date9__1'),
                    "date7__1": column_values.get('date7__1'),
                    "texto16__1": column_values.get('texto16__1'),
                    "dup__of_op__o_1c0__1": column_values.get('dup__of_op__o_1c0__1'),
                    "dup__of_op__o_2c__1": column_values.get('dup__of_op__o_2c__1'),
                    "dup__of_op__o_3c9__1": column_values.get('dup__of_op__o_3c9__1'),
                    "dup__of_op__o_1a__1": column_values.get('dup__of_op__o_1a__1'),
                    "dup__of_op__o_1c5__1": column_values.get('dup__of_op__o_1c5__1'),
                    "dup__of_op__o_1c__1": column_values.get('dup__of_op__o_1c__1'),
                    "dup__of_op__o_3a__1": column_values.get('dup__of_op__o_3a__1'),
                    "dup__of_op__o_3b__1": column_values.get('dup__of_op__o_3b__1'),
                    "dup__of_op__o_3c4__1": column_values.get('dup__of_op__o_3c4__1'),
                    "dup__of_op__o_3c__1": column_values.get('dup__of_op__o_3c__1'),
                    "text0__1": column_values.get('text0__1'),
                }
                         
                
                # Format date values for display
                result['data__1'] = formatar_data(result['data__1'])
                result['date3__1'] = formatar_data(result['date3__1'])
                result['date9__1'] = formatar_data(result['date9__1'])
                result['date7__1'] = formatar_data(result['date7__1'])

                logger.debug(f"Found item: {name} with ID: {item_id}")
            else:
                flash("Nenhum negócio encontrado com esse número", "warning")
                logger.warning(f"No business found with number: {num_negocio}")

        except Exception as e:
            flash(f"Erro ao buscar dados: {str(e)}", "danger")
            logger.error(f"Error retrieving data from Monday.com: {str(e)}")

    return render_template('readequacao.html', result=result)



@app.route('/submit_readequacao', methods=['POST'])
def submit_readequacao():
    try:
        # Get form data
        item_id = request.form.get('item_id')
        result_name = request.form.get('result_name')

        # Get date values
        novaDataEntregaAEREO = request.form.get('novaDataEntregaAEREO')
        novaDataEntregaTERRESTRE = request.form.get('novaDataEntregaTERRESTRE')
        novaDataEntregaCRIACAO = request.form.get('novaDataEntregaCRIACAO')
        novaDataEntregaSALES = request.form.get('novaDataEntregaSALES')

        # Get option values
        novaOpcao1A = request.form.get('novaOpcao1A')
        novaOpcao1B = request.form.get('novaOpcao1B')
        novaOpcao1C = request.form.get('novaOpcao1C')
        novaOpcao2A = request.form.get('novaOpcao2A')
        novaOpcao2B = request.form.get('novaOpcao2B')
        novaOpcao2C = request.form.get('novaOpcao2C')
        novaOpcao3A = request.form.get('novaOpcao3A')
        novaOpcao3B = request.form.get('novaOpcao3B')
        novaOpcao3C = request.form.get('novaOpcao3C')
        novaOpcao4A = request.form.get('novaOpcao4A')
        novaOpcao4B = request.form.get('novaOpcao4B')
        novaOpcao4C = request.form.get('novaOpcao4C')

        # Get file if uploaded
        file = request.files.get('file')

        logger.debug(f"Submitting readequacao for item ID: {item_id}")
        logger.debug(f"Form data: {request.form}")
        logger.debug(f"Form data: {file}")
        # Prepare column values for Monday.com update
        column_values = {}

        # Convert dates from DD/MM/YYYY to YYYY-MM-DD format for Monday.com API
        if novaDataEntregaAEREO and novaDataEntregaAEREO != "None":
            data__1 = convert_date_to_monday_format(novaDataEntregaAEREO)
            if data__1:
                column_values["data__1"] = {"date": data__1}

        if novaDataEntregaTERRESTRE and novaDataEntregaTERRESTRE != "None":
            date9__1 = convert_date_to_monday_format(novaDataEntregaTERRESTRE)
            if date9__1:
                column_values["date9__1"] = {"date": date9__1}

        if novaDataEntregaCRIACAO and novaDataEntregaCRIACAO != "None":
            date3__1 = convert_date_to_monday_format(novaDataEntregaCRIACAO)
            if date3__1:
                column_values["date3__1"] = {"date": date3__1}

        if novaDataEntregaSALES and novaDataEntregaSALES != "None":
            date7__1 = convert_date_to_monday_format(novaDataEntregaSALES)
            if date7__1:
                column_values["date7__1"] = {"date": date7__1}

        # Add text values to column_values only if they exist
        if novaOpcao1A and novaOpcao1A != "None":
            column_values["texto16__1"] = novaOpcao1A

        if novaOpcao2A and novaOpcao2A != "None":
            column_values["dup__of_op__o_1c0__1"] = novaOpcao2A

        if novaOpcao3A and novaOpcao3A != "None":
            column_values["dup__of_op__o_2c__1"] = novaOpcao3A

        if novaOpcao4A and novaOpcao4A != "None":
            column_values["dup__of_op__o_3c9__1"] = novaOpcao4A

        if novaOpcao1B and novaOpcao1B != "None":
            column_values["dup__of_op__o_1a__1"] = novaOpcao1B

        if novaOpcao1C and novaOpcao1C != "None":
            column_values["text0__1"] = novaOpcao1C

        if novaOpcao2B and novaOpcao2B != "None":
            column_values["dup__of_op__o_1c5__1"] = novaOpcao2B

        if novaOpcao2C and novaOpcao2C != "None":
            column_values["dup__of_op__o_1c__1"] = novaOpcao2C

        if novaOpcao3B and novaOpcao3B != "None":
            column_values["dup__of_op__o_3a__1"] = novaOpcao3B

        if novaOpcao3C and novaOpcao3C != "None":
            column_values["dup__of_op__o_3b__1"] = novaOpcao3C

        if novaOpcao4B and novaOpcao4B != "None":
            column_values["dup__of_op__o_3c4__1"] = novaOpcao4B

        if novaOpcao4C and novaOpcao4C != "None":
            column_values["dup__of_op__o_3c__1"] = novaOpcao4C

        # Update the item in Monday.com
        logger.debug(f"Updating item with column values: {column_values}")
        update_result = update_monday_item(item_id, MONDAY_BOARD_ID, column_values, API_KEY, API_URL)

        if update_result:
            logger.info(f"Successfully updated item: {item_id}")

            # Handle file upload if file was provided
            if file and allowed_file(file.filename):
                
                filename = secure_filename(file.filename)
                logger.info(f"Uploading file: {filename} to item: {item_id}")
                dir_path = os.path.dirname(os.path.realpath(__file__))
                static_path = os.path.join(dir_path, 'static')
                f = os.path.join(static_path, filename)

                try:
                    file.save(f)
                    logger.info(f"File saved to: {f}")
                    api_url = "https://api.monday.com/v2"
                    headers = {"Authorization": API_KEY}  # Content-Type will be set by requests

                    query_payload = {
                    "query" : f"""
                        mutation ($file: File!) {{
                            add_file_to_column (
                                file: $file,
                                item_id: "{item_id}",
                                column_id: "file_mkp3rd8p"
                            ) {{
                                id
                            }}
                        }}
                    """,
                    "variables": {
                            "file": None  
                        }
                    }

                    
                    opened_file = None
                    try:
                        opened_file = open(f, 'rb')
                        files = {
                            'query': (None, str(query_payload), 'application/json'),
                            'variables[file]': (filename, opened_file, 'multipart/form-data', {'Expires': '0'})
                            }
                        response = requests.post(api_url, headers=headers, files=files)
                        response.raise_for_status()  # Raise an exception for bad status codes
                        data = response.json()
                        logger.info(f"Monday.com API response: {data}")
                        if 'errors' in data:
                            logger.error(f"Error uploading to Monday.com: {data['errors']}")
                            logger.error(f"Error uploading to Monday.com: {data.get('errors')}")
                        else:
                             logger.info(f"File '{filename}' uploaded successfully to item {item_id}")
    
                    except Exception as e:
                        logger.error(f"Erro inesperado durante o upload do arquivo: {e}")
                        logger.error(f"Erro inesperado durante o upload do arquivo: {e}")
                    finally:
                         # Clean up the saved file after attempting upload
                         if os.path.exists(file_path_on_disk):
                        
        
                    
                            logger.debug(f"Prepared Request Headers: {prepared_request.headers}")
                            logger.debug(f"File upload response: {response.text}")
                            logger.debug(f"File upload reason: {response.reason}")
        
                    
                except requests.exceptions.RequestException as e:
                    logger.error(f"Erro na requisição de upload do arquivo: {str(e)}")
                    flash(f"Erro ao enviar e anexar arquivo: {str(e)}", "warning")
        
                except Exception as e:
                    logger.error(f"Erro inesperado durante o upload do arquivo: {str(e)}")
                    flash(f"Erro ao enviar e anexar arquivo: {str(e)}", "warning")
        
                flash("Dados atualizados com sucesso!", "success")
                return render_template('success.html', item_id=item_id, result_name=result_name)
            else:
                flash("Falha ao atualizar dados no Monday.com", "danger")
                logger.error("Failed to update item in Monday.com")
                return render_template('error.html', error="Falha ao atualizar dados no Monday.com")
    
    except Exception as e:
        logger.error(f"Error in submit_readequacao: {str(e)}")
        flash(f"Erro ao processar o formulário: {str(e)}", "danger")
        return render_template('error.html', error=str(e))

@app.errorhandler(413)
def request_entity_too_large(error):
    flash("Arquivo muito grande. Tamanho máximo: 16MB", "danger")
    return redirect(url_for('readequacao'))

@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html', error="Página não encontrada"), 404

@app.errorhandler(500)
def internal_server_error(error):
    return render_template('error.html', error="Erro interno do servidor"), 500

ITEM_ID = 7815005218
COLUMN_ID = "file_mkp3rd8p"
UPLOAD_URL = "https://api.monday.com/v2/file"
FILE_PATH = "static/logo.png"  # Assuming logo.png is in a 'static' folder


if not os.path.exists(FILE_PATH):
    print(f"Error: File not found at {FILE_PATH}")
else:
    headers = {'Authorization': API_KEY}
    files = {'file': ('logo.png', open(FILE_PATH, 'rb'), 'image/png')}

    try:
        response = requests.post(UPLOAD_URL, headers=headers, files=files)
        print(f"Upload Status Code: {response.status_code}")
        print(f"Upload Response: {response.text}")

        if response.ok:
            try:
                response_data = response.json()
                if 'data' in response_data and 'id' in response_data['data']:
                    asset_id = response_data['data']['id']
                    print(f"File uploaded successfully, asset ID: {asset_id}")

                    mutation_query = f"""
                        mutation {{
                            add_file_to_column (
                                asset_id: {asset_id},
                                item_id: {ITEM_ID},
                                column_id: "{COLUMN_ID}"
                            ) {{
                                id
                            }}
                        }}
                    """
                    headers_graphql = {'Authorization': API_KEY, 'Content-Type': 'application/json'}
                    payload = {'query': mutation_query}
                    attach_response = requests.post("https://api.monday.com/v2", headers=headers_graphql, json=payload)
                    attach_response_json = attach_response.json()
                    print(f"Attach Response: {attach_response_json}")

                    if 'errors' in attach_response_json:
                        print(f"File attach failed: {attach_response_json['errors']}")
                    elif 'data' in attach_response_json and 'add_file_to_column' in attach_response_json['data']:
                        print("File attached successfully!")
                    else:
                        print("Unexpected attach response.")
                else:
                    print("Unexpected upload response structure.")
            except Exception as e:
                print(f"Error processing upload response: {e}")
        else:
            print(f"File upload failed with status code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Request exception: {e}")
