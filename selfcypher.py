#selfcypher.py
from flask import Flask, render_template, request, send_file
import datetime
import io
import itertools


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
#def generate():
    # data = request.json  # Change this to handle JSON data

    # # Generate the content of the text file
    # passwords = generate_passwords(data)

    # # Create the content of the text file
    # text_content = "\n".join(passwords)

    # # Create an in-memory text stream
    # text_stream = io.StringIO(text_content)

    # # Use send_file to send the in-memory text stream as a file
    # return send_file(
    #     io.BytesIO(text_stream.getvalue().encode()),
    #     as_attachment=True,
    #     download_name='generated_passwords.txt',
    #     mimetype='text/plain'
    # )
def generate():
    data = request.json
    passwords = generate_passwords(data)

    def generate_file_content():
        for password in passwords:
            yield f"{password}\n"

    response = Response(generate_file_content(), mimetype='text/plain')
    response.headers['Content-Encoding'] = 'gzip'
    return response


def generate_passwords(data):
    passwords = set()
    
    # Basic information
    names = [data.get('firstname', ''), data.get('midname', ''), data.get('lastname', '')]
    names = [name.lower() for name in names if name]
    special_chars = ['@', '#', '$', '%', '^', '&', '*', '!','_','-']
    phone_numbers = get_multiple_values(data, 'phonenum')
    emails = get_multiple_values(data, 'email')
    other_dates = get_multiple_values(data, 'odates')
    relative_names = get_multiple_values(data, 'relname')
    favorite_foods = get_multiple_values(data, 'favfood')
    favorite_locations = get_multiple_values(data, 'favloc')
    extra_words = get_multiple_values(data, 'extra')
    house_number = data.get('hnum', '')
    city = data.get('city', '')
    postal_code = data.get('pincode', '')
    state = data.get('state', '')
    country = data.get('country', '')
    company = data.get('company', '')
    job_title = data.get('jobtitle', '')
    religion = data.get('religion', '')
    
    all_words = names + relative_names + favorite_foods + favorite_locations + extra_words + [
    house_number, city, postal_code, state, country, company, job_title, religion
] + [religion]
    all_words = [word for word in all_words if word] + extra_words

    # Date of birth
    dates = []
    if data.get('dob'):
        dob = datetime.datetime.strptime(data['dob'], '%Y-%m-%d')
        dates = [
            dob.strftime('%Y'),
            dob.strftime('%d%m'),
            dob.strftime('%y'),
            dob.strftime('%m%d'),
            dob.strftime('%d%m%Y'),
            dob.strftime('%d%m%y'),
        ]

    o_dates = []
    for date_str in other_dates:
        try:
            date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
            dates.extend([
                date.strftime('%Y'),
                date.strftime('%d%m'),
                date.strftime('%y'),
                date.strftime('%m%d'),
                date.strftime('%d%m%Y'),
                date.strftime('%d%m%y'),
            ])
        except ValueError:
            pass
    
    # Phone number variations
    phone_variations = []
    for phone in phone_numbers:
        phone_variations.append(phone[:3])  # First 3 digits
        phone_variations.append(phone[-3:])  # Last 3 digits
        phone_variations.append(phone[:4])  # First 4 digits
        phone_variations.append(phone[-4:])  # Last 4 digits
    
    # Vehicle number variations
    # vehicle_variations = []
    # for vehicle in data.get('vehiclenum', '').split(','):
    #     vehicle = vehicle.strip()
    #     if vehicle:
    #         vehicle_variations.append(vehicle[-4:])  # Last 4 characters
    
    # Email variations
    email_variations = []
    for email in emails:
        username = email.split('@')[0]
        email_variations.extend(get_unique_parts(username))

    if postal_code:
        postal_numbers = [postal_code[-2:], postal_code[:2], postal_code[-4:], postal_code[:4]]
    else:
        postal_numbers = []
    
    # Generate combinations
    for word in all_words:
        for date in dates + o_dates:
            for char in special_chars:
                for case in [word.lower(), word.title(), word.upper()]:
                    passwords.add(f"{case}{char}{date}")
                    #passwords.add(f"{date}{char}{case}")
        
        for phone in phone_variations:
            for char in special_chars:
                for case in [word.lower(), word.title(), word.upper()]:
                    passwords.add(f"{case}{char}{phone}")
                    #passwords.add(f"{phone}{char}{case}")
        
        # for vehicle in vehicle_variations:
        #     for char in special_chars:
        #         for case in [word.lower(), word.title(), word.upper()]:
        #             passwords.add(f"{case}{char}{vehicle}")
        #             passwords.add(f"{vehicle}{char}{case}")
        
        for email_part in email_variations:
            for char in special_chars:
                for case in [word.lower(), word.title(), word.upper()]:
                    passwords.add(f"{case}{char}{email_part}")
                    #passwords.add(f"{email_part}{char}{case}")

    for word in all_words:
        for date in dates:
            for char in special_chars:
                passwords.add(f"{word}{char}{date}")
        
        for number in postal_numbers + phone_numbers:
            passwords.add(f"{word}{number}")
            for char in special_chars:
                passwords.add(f"{word}{char}{number}")

    # Generate passwords from extra words
    for word in extra_words:
        for date in dates:
            for char in special_chars:
                passwords.add(f"{word}{char}{date}")
        
        for number in postal_numbers + phone_numbers:
            passwords.add(f"{word}{number}")
            for char in special_chars:
                passwords.add(f"{word}{char}{number}")

    def generate_number_sequences(max_length=4):
        for length in range(1, max_length + 1):
            for combo in itertools.product('0123456789', repeat=length):
                yield ''.join(combo)
        for digit in '0123456789':
            for length in range(2, max_length + 1):
                yield digit * length

    def generate_special_sequences(max_length=4):
        even_numbers = '02468'
        odd_numbers = '13579'
        for numbers in (even_numbers, odd_numbers):
            for length in range(1, max_length + 1):
                for combo in itertools.combinations(numbers, length):
                    yield ''.join(combo)

    # Generate passwords in batches
    def generate_password_batches(batch_size=10000):
        batch = set()
        for word in all_words:
            for seq in itertools.chain(generate_number_sequences(), generate_special_sequences()):
                batch.add(f"{word}{seq}")
                #batch.add(f"{seq}{word}")
                for char in special_chars:
                    batch.add(f"{word}{char}{seq}")
                    #batch.add(f"{seq}{char}{word}")
                
                if len(batch) >= batch_size:
                    yield batch
                    batch = set()
        
        if batch:
            yield batch

    # Process passwords in batches
    for batch in generate_password_batches():
        passwords.update(batch)


    number_sequences = generate_number_sequences()
    special_sequences = generate_special_sequences()
    all_sequences = list(set(itertools.chain(number_sequences, special_sequences)))

    for word in all_words:
    # Append numbers and special sequences
        for seq in all_sequences:
            for case in [word.lower(), word.title(), word.upper()]:
                passwords.add(f"{case}{seq}")
            
        # Prepend numbers and special sequences
        for seq in all_sequences:
            for case in [word.lower(), word.title(), word.upper()]:
                passwords.add(f"{seq}{case}")
            
        # Append special character + numbers/special sequences
        for char in special_chars:
            for seq in all_sequences:
                for case in [word.lower(), word.title(), word.upper()]:
                    passwords.add(f"{case}{char}{seq}")
            
        # Prepend numbers/special sequences + special character
        # for char in special_chars:
        #     for seq in all_sequences:
        #         for case in [word.lower(), word.title(), word.upper()]:
        #             passwords.add(f"{seq}{char}{case}")


    
    # Filter passwords shorter than 8 characters
    passwords = [pw for pw in passwords if len(pw) >= 8]
    
    return list(passwords)

def get_multiple_values(data, key):
    return [value.strip() for value in data.get(key, []) if value.strip()]

def get_unique_parts(username):
    parts = username.split('.')
    unique_parts = []
    for part in parts:
        if part not in unique_parts:
            unique_parts.append(part)
    return unique_parts

if __name__ == '__main__':
    app.run(debug=True)