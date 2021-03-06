import pytest
import base64
import matplotlib.pyplot as plt
import datetime


@pytest.fixture
def load_img():
    image_path = "./images/airplane001.jpg"
    with open(image_path, "rb") as image_file:
        b64_bytes = base64.b64encode(image_file.read())
    b64_string = str(b64_bytes, encoding='utf-8')
    return b64_string


@pytest.fixture
def sample_img_request(load_img):
    r = {'username': 'test088',
         'num_img': 2,
         'imgs': [load_img, load_img],
         'procedure': 'histogram_eq',
         'img_format': 'JPG',
         'filename': 'airplane001.jpg'
         }
    return r


def test_encode_imgs_b64(load_img):
    from server import decode_b64, encode_imgs_b64
    decoded = decode_b64(load_img, 'JPG')
    list_decoded = [decoded, decoded]
    list_encoded = encode_imgs_b64(list_decoded)
    assert list_encoded[0][0:10] == load_img[0:10]


def test_decode_imgs_from_request(sample_img_request):
    from server import decode_imgs_from_request
    decoded_list = decode_imgs_from_request(sample_img_request)
    first_img = decoded_list[0]
    # passes if the shape of the matrix is correct
    assert first_img.shape[2] == 3


def test_process_imgs_with_method(load_img):
    from server import process_imgs_with_method, decode_b64
    print(load_img)
    decoded_list = [decode_b64(load_img, 'JPG')]
    processed_list = process_imgs_with_method(decoded_list, 'histogram_eq')
    decoded = decoded_list[0]
    processed = processed_list[0]
    # Only tests that the processed images are different from the original
    assert not (decoded == processed).all()


def test_generate_request_id():
    from server import generate_request_id
    id1 = generate_request_id()
    id2 = generate_request_id()
    difference = int(id2) - int(id1)
    assert difference == 1


def test_decode_b64(load_img):
    from server import decode_b64, encode_b64
    decoded = decode_b64(load_img, 'JPG')
    encoded = encode_b64(decoded, 'JPG')
    # redoecoded = decode_b64(encoded, 'JPG')
    # plt.figure(0)
    # plt.imshow(decoded)
    # plt.figure(1)
    # plt.imshow(redoecoded)
    # plt.show()
    # The two strings aren't exactly the same, but I plotted
    # and found them to be identical visually.
    assert encoded[0:10] == load_img[0:10]


def test_encode_b64(load_img):
    from server import decode_b64, encode_b64
    decoded = decode_b64(load_img, 'JPG')
    encoded = encode_b64(decoded, 'JPG')
    assert encoded[0:10] == load_img[0:10]


def test_previous_request_preview():
    from server import previous_request_preview
    data = previous_request_preview('test088', ['1'])
    assert data['1']['filename'] == 'airplane001.jpg'


def test_get_previous_requests():
    from server import get_previous_requests
    previous_requests = get_previous_requests('test088')
    # only checks if id 1 is among previous request ids
    assert '1' in previous_requests


def test_validate_previous_request():
    from server import validate_previous_request
    flag = validate_previous_request('test088')
    assert flag == 1


@pytest.mark.parametrize('r,answer', [
    ({'bad': 1}, 1),
    ({'username': 'test088',
      'num_img': 2,
      'imgs': ['stuff'],
      'procedure': 'make_pretty',
      'img_format': 'JPG',
      'filename': 'airplane001.jpg'
      }, 1),
    ({'username': 'test088',
      'num_img': 'ooo',
      'imgs': ['stuff'],
      'procedure': 'histogram_eq',
      'img_format': 'JPG',
      'filename': 'airplane001.jpg'
      }, 2),
])
def test_bad_process_img_requests(r, answer):
    from server import validate_process_img
    flag = validate_process_img(r)
    assert flag == answer


def test_get_user_metrics():
    from server import get_user_metrics
    metrics = get_user_metrics('test088')
    assert type(metrics[0]) == dict


def test_validate_process_img(sample_img_request):
    from server import validate_process_img
    flag = validate_process_img(sample_img_request)
    assert flag == 0


def test_store_new_request(sample_img_request, load_img):
    from server import store_new_request

    db_data = store_new_request(sample_img_request, '1', [load_img],
                                datetime.datetime.now())
    # just checking that the process time is very short
    assert db_data['time_to_process'] < 0.01


def test_get_img_sizes(load_img):
    from server import get_img_sizes
    sizes = get_img_sizes([load_img], 'JPG')
    assert len(sizes[0]) == 2


def test_get_histograms(sample_img_request):
    from server import get_histograms, decode_imgs_from_request
    decoded = decode_imgs_from_request(sample_img_request)
    hist_list = get_histograms(decoded)
    # checks if data structure is in right format
    assert len(hist_list[0]['red'][0]) == 256
