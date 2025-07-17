import boto3
from flask import Flask, request, render_template_string
from werkzeug.utils import secure_filename

# Configuration
app = Flask(__name__)
BUCKET_NAME = 'your-s3-bucket-name'  # 🔁 Replace with your actual bucket name
REGION = 'ap-south-1'                # 🔁 Replace with your AWS region

s3 = boto3.client('s3', region_name=REGION)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head><title>Upload Image</title></head>
<body>
    <h2>Upload an Image</h2>
    <form method="post" enctype="multipart/form-data">
        <input type="file" name="image" accept="image/*" required>
        <input type="submit" value="Upload">
    </form>
    {% if image_url %}
        <h3>Uploaded Image:</h3>
        <img src="{{ image_url }}" width="300">
        <p>URL: <a href="{{ image_url }}">{{ image_url }}</a></p>
    {% endif %}
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def upload_image():
    image_url = None
    if request.method == 'POST':
        if 'image' not in request.files:
            return "No file part"
        file = request.files['image']
        if file.filename == '':
            return "No selected file"
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            s3.upload_fileobj(
                file,
                BUCKET_NAME,
                filename,
                ExtraArgs={
                    'ACL': 'public-read',
                    'ContentType': file.content_type
                }
            )
            image_url = f"https://{BUCKET_NAME}.s3.{REGION}.amazonaws.com/{filename}"
    return render_template_string(HTML_TEMPLATE, image_url=image_url)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
