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
    if valor is None or valor == "None":
        return '-'
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
                    "dup__of_op__o_2c__1", "dup__of_op__o_3c9__1"
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
        novaOpcao2A = request.form.get('novaOpcao2A')
        novaOpcao3A = request.form.get('novaOpcao3A')
        novaOpcao4A = request.form.get('novaOpcao4A')
        
        # Get file if uploaded
        file = request.files.get('file')
        
        logger.debug(f"Submitting readequacao for item ID: {item_id}")
        logger.debug(f"Form data: {request.form}")
        
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
        
        # Add text values to column_values
        if novaOpcao1A and novaOpcao1A != "None":
            column_values["texto16__1"] = novaOpcao1A
        else:
            column_values["texto16__1"] = ""
            
        if novaOpcao2A and novaOpcao2A != "None":
            column_values["dup__of_op__o_1c0__1"] = novaOpcao2A
        else:
            column_values["dup__of_op__o_1c0__1"] = ""
            
        if novaOpcao3A and novaOpcao3A != "None":
            column_values["dup__of_op__o_2c__1"] = novaOpcao3A
        else:
            column_values["dup__of_op__o_2c__1"] = ""
            
        if novaOpcao4A and novaOpcao4A != "None":
            column_values["dup__of_op__o_3c9__1"] = novaOpcao4A
        else:
            column_values["dup__of_op__o_3c9__1"] = ""
        
        # Update the item in Monday.com
        logger.debug(f"Updating item with column values: {column_values}")
        update_result = update_monday_item(item_id, MONDAY_BOARD_ID, column_values, API_KEY, API_URL)
        
        if update_result:
            logger.info(f"Successfully updated item: {item_id}")
            
            # Handle file upload if file was provided
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                logger.info(f"Uploading file: {filename} to item: {item_id}")
                
                try:
                    # Save file to a temporary location
                    assets_dir = os.path.join(app.root_path, 'assets')
                    os.makedirs(assets_dir, exist_ok=True)  # Create the directory if it doesn't exist
                    local_filepath = os.path.join(assets_dir, filename)
                    file.save(local_filepath)
                    
                    try:
                        # This is a final attempt based on Monday.com's official documentation
                        # for file uploads using their GraphQL API
                        logger.info(f"Attempting file upload from: {local_filepath}")

                        api_url = "https://api.monday.com/v2"
                        
                        # First, let's try using the mutation directly for file uploads
                        # Step 1: Create the file in Monday.com storage
                            with open(local_filepath, 'rb') as f:
                                operations = json.dumps({
                                    "query": "mutation add_file($file: File!, $itemId: Int!, $columnId: String!) { add_file_to_column (item_id: $itemId, column_id: $columnId, file: $file) {id}}",
                                    "variables": {
                                        "file": None,
                                        "itemId": int(item_id),
                                        "columnId": "file_mkp3rd8p"
                                    }
                                })

                                map_json = json.dumps({
                                    "0": ["variables.file"]
                                })
                            
                                # Create a multipart form-data request with the file as Monday.com expects
                                files = {
                                    'operations': (None, operations),
                                    'map': (None, map_json),
                                    '0': (filename, f, file.content_type)
                                }
                                
                                headers = {
                                    'Authorization': API_KEY  # Only authorization, let requests set the content type
                                }
                                
                                logger.info(f"Sending file upload request with Monday.com's expected format")
                                logger.info(f"URL: {api_url}")
                                logger.info(f"Operations: {operations}")
                                logger.info(f"Map: {map_json}")
                                logger.info(f"File keys: {files.keys()}")
                                
                                # Make a simple POST request with file data
                                response = requests.post(
                                    api_url,
                                    headers=headers,
                                    files=files
                                )
                        finally:
                            # Always clean up the temporary file
                            try:
                                if os.path.exists(temp_filepath):
                                    os.remove(temp_filepath)
                            except Exception as e:
                                logger.error(f"Error removing temporary file: {str(e)}")
                        
                        response_data = response.json() if response.text else {}
                        
                        if response.status_code == 200 and not response_data.get('errors'):
                            logger.info(f"File uploaded successfully: {response_data}")
                            flash("Dados e arquivo atualizados com sucesso!", "success")
                        else:
                            error_details = response_data.get('errors', [{'message': 'Unknown error'}])[0].get('message', 'Unknown error')
                            logger.error(f"File upload failed (Status: {response.status_code}): {error_details}")
                            logger.error(f"Full response: {response.text}")
                            flash(f"Dados atualizados, mas falha ao enviar arquivo! {error_details}", "warning")
                            
                    except Exception as e:
                        logger.error(f"Error uploading file: {str(e)}")
                        flash(f"Dados atualizados, mas erro ao enviar arquivo: {str(e)}", "warning")
                else:
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
