import io
import base64
import qrcode

def generate_pet_qr_code(emergency_url):
    """
    Generates a QR Code image for a pet's public emergency contact URL.
    Returns a base64 data URI string for embedding directly in <img src="..." />.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(emergency_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#10b981", back_color="#ffffff")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{img_str}"
