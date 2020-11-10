from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import HTMLResponse
import json
import yaml
import os

CHUNK_LENGTH = 10000

app = FastAPI()


def get_key_list(key):
    if key[0] == '[' and key[-1] == ']':
        key = key[1:-1]
    key = key.split(',')
    for i in range(len(key)):
        key[i] = key[i].strip()
        if key[i].isdigit() or key[i].startswith('-') and key[1:].isdigit():
            key[i] = int(key[i])
        else:
            key[i] = str(key[i])
            if key[i][0] == '\'' or key[i][0] == '"':
                key[i] = key[i][1:]
            if key[i][-1] == '\'' or key[i][-1] == '"':
                key[i] = key[i][:-1]
    return key


def get_data(path_to_file, key, file_type):
    with open(path_to_file) as file:
        if file_type == 'json':
            data = json.load(file)
        else:
            data = yaml.full_load(file)
    return data


def get_value(data, key):
    for key_element in key:
        data = data[key_element]
    return data


def seek(path_to_file, key):
    filename, file_extension = os.path.splitext(path_to_file)
    file_extension = file_extension.lower()
    if file_extension == '.json':
        file_type = 'json'
    elif file_extension in ['.yaml', '.yml']:
        file_type = 'yaml'
    else:
        raise NameError

    key_list = get_key_list(key)

    data = get_data(path_to_file, key, file_type)

    value = get_value(data, key_list)
    return value


@app.post("/")
async def process_file(upload_file: UploadFile = File(...), file_key: str = Form(...)):
    with open(upload_file.filename, 'wb') as f:
        [f.write(chunk) for chunk in iter(
            lambda: upload_file.file.read(CHUNK_LENGTH), b'')]
    value = seek(upload_file.filename, file_key)
    os.remove(upload_file.filename)
    return value


@app.get("/")
async def main():
    content = """
<body>
<form action="/" enctype="multipart/form-data" method="post">
<input name="upload_file" type="file">
<input name="file_key" type="text">
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)
