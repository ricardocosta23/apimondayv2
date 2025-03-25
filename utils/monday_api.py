import requests
import json
import logging

logger = logging.getLogger(__name__)

def get_monday_data(query, api_key, api_url, variables=None):
    """
    Function to make API calls to Monday.com
    
    Args:
        query (str): GraphQL query to execute
        api_key (str): Monday.com API key
        api_url (str): Monday.com API URL
        variables (dict, optional): Variables for the query
        
    Returns:
        dict: Response from Monday.com API
    """
    headers = {"Authorization": api_key, "Content-Type": "application/json"}
    payload = {'query': query}
    
    if variables:
        payload['variables'] = variables
        
    try:
        response = requests.post(url=api_url, json=payload, headers=headers)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error making request to Monday.com API: {str(e)}")
        if hasattr(e, 'response') and e.response:
            logger.error(f"Response: {e.response.text}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON response: {str(e)}")
        raise

def update_monday_item(item_id, board_id, column_values, api_key, api_url):
    """
    Updates a Monday.com item with the provided column values
    
    Args:
        item_id (str): ID of the item to update
        board_id (int): ID of the board containing the item
        column_values (dict): Dictionary of column values to update
        api_key (str): Monday.com API key
        api_url (str): Monday.com API URL
        
    Returns:
        bool: True if update was successful, False otherwise
    """
    try:
        # Convert the column_values dict to a JSON string
        column_values_json = json.dumps(column_values)
        
        # Create the GraphQL mutation
        mutation = f"""
        mutation {{
          change_multiple_column_values (
            item_id: {item_id}, 
            board_id: {board_id}, 
            column_values: {json.dumps(column_values_json)}
          ) {{
            id
          }}
        }}
        """
        
        logger.debug(f"Mutation: {mutation}")
        
        # Make the API call
        headers = {"Authorization": api_key, "Content-Type": "application/json"}
        payload = {'query': mutation}
        
        response = requests.post(url=api_url, json=payload, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        logger.debug(f"Update response: {result}")
        
        # Check if the update was successful
        if result.get('data', {}).get('change_multiple_column_values', {}).get('id'):
            return True
        else:
            logger.error(f"Failed to update item. Response: {result}")
            return False
            
    except Exception as e:
        logger.error(f"Error updating Monday.com item: {str(e)}")
        return False
