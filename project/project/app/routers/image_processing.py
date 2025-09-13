from fastapi import APIRouter, UploadFile
from app.services.image_service import process_image  # ensure this exists
import tempfile
import os

router = APIRouter()

@router.post("/image-input")
async def image_input(file: UploadFile):
    try:
        # Debug: print filename
        print("Received file:", file.filename)
        
        # Acceptable extensions
        ext = os.path.splitext(file.filename)[-1].lower()
        if ext not in [".jpg", ".jpeg", ".png"]:
            return {"error": f"Unsupported file type: {ext}"}

        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
            print("Temp file created at:", tmp_path)

        # Call image processing function
        result = await process_image(tmp_path)  # if process_image is async
        print("Image processing complete")

        return {"result": result}

    except Exception as e:
        print("ERROR in image_input:", str(e))
        return {"error": str(e)}
    finally:
        # Clean up temp file
        try:
            os.remove(tmp_path)
        except:
            pass
