import os
from google.cloud import vision
import argparse  

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.join(os.curdir, 'master-purpose-403922-ec8ea7452d1b.json')

client = vision.ImageAnnotatorClient()

def annotate(image_url: str, uploaded_file) -> vision.WebDetection:
    """Returns web annotations given the path to an image.

    Args:
        image_url: URL of the input image.
        uploaded_file: Uploaded file.

    Returns:
        An WebDetection object with relevant information of the
        image from the internet (i.e., the annotations).
    """
    client = vision.ImageAnnotatorClient()

    if image_url:
        image = vision.Image()
        image.source.image_uri = image_url
    elif uploaded_file:
        content = uploaded_file.read()
        image = vision.Image(content=content)
    else:
        return None

    web_detection = client.web_detection(image=image).web_detection

    return web_detection



def report(annotations: vision.WebDetection) -> dict:
    results = {
        'full_matches': [],
        'web_entities': []
    }

    if not annotations:
        return results

    if annotations.full_matching_images:
        # Pegue apenas a primeira imagem correspondente
        results['full_match'] = annotations.full_matching_images[0].url

    if annotations.web_entities:
        # Limita a três entidades da web
        results['web_entities'] = [{'description': entity.description, 'score': entity.score} for entity in annotations.web_entities[:3]]

    return results



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    path_help = str(
        "The image to detect, can be web URI, "
        "Google Cloud Storage, or path to local file."
    )
    parser.add_argument("image_url", help=path_help)
    args = parser.parse_args()

    report(annotate(args.image_url))

    """  python web_detect.py "https://www.thesprucepets.com/thmb/ogpjgm6PgjX0ukeCun6E2OE8zaY=/2326x1288/filters:fill(auto,1)/GettyImages-1171092661-7813725c40f9443f970ed85d78b8830e.jpg" """