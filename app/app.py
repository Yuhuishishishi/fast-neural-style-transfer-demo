from flask import Flask, render_template, request, redirect
import os.path
import subprocess
import uuid
from flask_wtf import FlaskForm
from wtforms import FileField, SelectField, SubmitField
from wtforms.validators import DataRequired

cli_base_dir = os.path.dirname(os.path.dirname(__file__))
cli_base_dir = os.path.abspath(os.path.join(cli_base_dir, "cli_tool"))

# initialize flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'

STYLE_MODELS = {
    "candy": "candy.pth",
    "mosaic": "mosaic.pth",
    "rain_princess": "rain_princess.pth",
    "udnie": "udnie.pth",
    "sketch": "sketch.pth",
}

UPLOAD_PATH = os.path.join(app.static_folder, 'tmp_img', "upload_image")


class ImageSelection(FlaskForm):
    upload_image = FileField('Upload_image', validators=[DataRequired()])
    style = SelectField("Select style to transfer", validators=[DataRequired()],
                        choices=list(zip(STYLE_MODELS.values(),
                                         STYLE_MODELS.keys())))
    submit = SubmitField('Transfer Image')


@app.route("/", methods=["GET", "POST"])
def transfer():
    form = ImageSelection()
    if form.validate_on_submit():
        # save the file to temp folder
        image_data = request.files[form.upload_image.name].read()
        upload_image_name = str(uuid.uuid4()) + ".jpg"
        upload_path = os.path.join(UPLOAD_PATH, upload_image_name)
        open(upload_path, 'wb').write(image_data)

        # run the transfer
        gen_image_name = transfer_image(upload_path, form.style.data)

        # trim the upload image
        upload_path = os.path.join(
            "tmp_img/upload_image/",
            os.path.basename(upload_path)
        )

        return render_template("transfer.html", form=form,
                               gen_img_name=gen_image_name, orig_img_name=upload_path)
    return render_template("transfer.html", form=form)


def get_upload_image_path(image_name):
    return os.path.join(app.static_folder, f"tmp_img/upload_image/{image_name}")


def transfer_image(content_image, style_image_model_name):
    gen_image_name = "gen_" + str(uuid.uuid4()) + ".jpg"

    cmd = f"""
        python {os.path.join(cli_base_dir, "neural_style", "neural_style.py")} eval --content-image {content_image} \
        --output-image {os.path.join(app.static_folder, "tmp_img/gen_image", gen_image_name)} \
        --model {os.path.join(cli_base_dir, "saved_models", style_image_model_name)} --cuda 0
    """.strip()

    print(cmd)

    _ = subprocess.run(cmd, shell=True)

    return os.path.join("tmp_img/gen_image", gen_image_name)
