from flask import Flask, redirect, url_for, session, request , render_template 
from flask_oauthlib.client import OAuth
from code_manager import CodeManager
import secrets
import pandas as pd
from google.oauth2 import service_account
import googleapiclient.discovery
import io
import subprocess


app = Flask(__name__)
app.secret_key = 'line-test'

code_manager = CodeManager()

credentials = service_account.Credentials.from_service_account_file(
    "E:\MyBEER\json\mybeer-project-8e1bbcd5496e.json",
    scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive.file']
)

# Set your spreadsheet ID and range
spreadsheet_id = '18prCrDXazfp_DkxaqC9e6qOHh7mpX4nNb8uoGNW-eDY'
range_name = 'MyBEER'  # Change to your sheet name


oauth = OAuth(app)

line = oauth.remote_app(
    'line',
    consumer_key='2001865066',
    consumer_secret='03a9a3690f39dceab47bd37d4a8bbbf2',
    request_token_params=None,
    base_url='https://api.line.me/v2/',
    authorize_url='https://access.line.me/oauth2/v2.1/authorize',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://api.line.me/oauth2/v2.1/token',
)

@app.route('/')
def home():
    # Check if the user is already logged in
    if 'line_token' in session:
        # User is already logged in, redirect to a different route (e.g., 'index')
        return redirect(url_for('index'))
    else:
        # User is not logged in, redirect to the login page
        return redirect(url_for('login'))


@app.route('/login')
def login():
    # Generate a random state string
    state = secrets.token_urlsafe(16)
    
    # Store the state in the session for later validation
    session['oauth_state'] = state
    
    # Specify the required scope
    scope = 'openid profile email'  # Adjust the scope as needed
    
    return line.authorize(callback=url_for('authorized', _external=True), state=state, scope=scope )

@app.route('/logout' , methods=['GET', 'POST'])
def logout():
    session.pop('line_token', None)
    return redirect(url_for('login'))




@app.route('/login/authorized')
def authorized():
    # Validate the state parameter
    stored_state = session.pop('oauth_state', None)
    received_state = request.args.get('state')

    if stored_state is None or received_state != stored_state:
        return 'Access denied: Invalid state or missing access token.'

    resp = line.authorized_response()

    if resp is None or 'access_token' not in resp:
        return 'Access denied: Invalid state or missing access token.'

    # Continue with your authorization process
    print(resp['id_token'])
    print(resp['access_token'])

    session['line_token'] = (resp['access_token'], '')
    session['user_id'] = resp['id_token']
    session['user_display_name'] = resp['id_token']

    return redirect(url_for('index'))



@app.route('/index')
def index():
    print(session['line_token'])
    if 'line_token' not in session:
        # User is not logged in, redirect to the login page
        return redirect(url_for('login'))
    
    # User is logged in, continue with the index page
    resp = line.authorized_response()
    return render_template('index.html')




@app.route('/submit', methods=['POST', 'GET'])
def submit():
    data = request.form.to_dict()
    image_file = request.files['image']
    image_data = image_file.read()

    # Call a function to write data to Google Sheets
    success, msg, code = write_to_google_sheets(data, image_data, code_manager)
    if success:
        return render_template('index.html', msg=msg , code=code)
    else:
        return render_template('index.html', msg=msg)

def write_to_google_sheets(data, image_data, code_manager):
    service = googleapiclient.discovery.build('sheets', 'v4', credentials=credentials)
    user_id = session.get('user_id')

    # Check if there are available codes before anything else
    if code_manager.is_empty():
        return False, 'โค้ดหมดแล้ว', None

    # Check if the user_id already exists in the Google Sheet
    try:
        request = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range='MyBEER'  # Adjust the sheet name and range accordingly
        )
        response = request.execute()
        values = response.get('values', [])
        user_ids = [row[0] for row in values]
    except Exception as e:
        # Handle exception appropriately
        print(f"Error: {e}")
        return False, f"Error accessing Google Sheet. Please try again later.", None

    if user_id in user_ids:
        return False, 'คุณได้ใช้สิทธินี้ไปแล้ว', None

    # Upload the image to Google Drive and get the link
    folder_id = '1kWAqsGKd1Od9VItL2GGk6KhzG2lgQNlq'
    image_link = upload_to_google_drive(image_data, folder_id)

    # Get a code from the CodeManager
    code = code_manager.get_available_code()
    
    if code:
        # Move the code to another list (e.g., used_items)
        code_manager.add_used_code(code)

        # Prepare the data for writing, including the image link and code
        values = [[user_id, data.get('name', ''), data.get('surname', ''), data.get('phone', ''),
                   data.get('age', ''), data.get('merchant', ''), code, image_link]]

        # Write the data to the spreadsheet
        request = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='RAW',
            body={'values': values}
        )
        response = request.execute()

        # If the submission is successful
        if response.get('updates', {}).get('updatedCells', 0) > 0:
            return True, 'Submission successful!', code
        else:
            return False, 'Error submitting data to Google Sheet.', None
    else:
        return False, 'โค้ดหมดแล้ว', None







def upload_to_google_drive(image_data, folder_id):
    user_id = session.get('user_id')
    drive_service = googleapiclient.discovery.build('drive', 'v3', credentials=credentials)

    file_metadata = {
        'name': f'{user_id}.jpg',  
        'mimeType': 'image/jpeg',
        'parents': [folder_id]  
    }

    # Use image_data directly in MediaIoBaseUpload
    media = googleapiclient.http.MediaIoBaseUpload(io.BytesIO(image_data), mimetype='image/jpeg')

    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    image_link = f'https://drive.google.com/uc?id={file["id"]}'
    return image_link


def run_python_script():
    result = subprocess.check_output(['python', 'index.py'])
    return result


if __name__ == '__main__':
    app.run(debug=True)
