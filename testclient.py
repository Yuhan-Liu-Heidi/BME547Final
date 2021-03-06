import base64
import io
from matplotlib import pyplot as plt
import matplotlib.image as mpimg
from skimage import exposure
from skimage import data, img_as_float
import requests

address = "http://localhost:5000"


def read_file_as_b64(image_path):
    with open(image_path, "rb") as image_file:
        b64_bytes = base64.b64encode(image_file.read())
        # print(image_file.read())
    # print(b64_bytes)
    b64_string = str(b64_bytes, encoding='utf-8')
    return b64_string


def decode_b64(base64_string, img_format):
    image_bytes = base64.b64decode(base64_string)
    image_buf = io.BytesIO(image_bytes)
    return mpimg.imread(image_buf, format=img_format)


def save_b64_image(base64_string):
    image_bytes = base64.b64decode(base64_string)
    with open("new-img.jpg", "wb") as out_file:
        out_file.write(image_bytes)
    return


def hist_equal_filter(before_filtering):
    return exposure.equalize_hist(before_filtering)


def local_load_filter_display(base64_string):
    img = decode_b64(base64_string, 'JPG')
    after_filtering = hist_equal_filter(img)
    fig, ax = plt.subplots(2, 2)
    ax[0, 0].imshow(img)
    ax[0, 1].imshow(after_filtering)
    img_hist, img_bins = exposure.histogram(after_filtering)
    ax[1, 0].plot(img_bins, img_hist)
    plt.show()
    print()


def remote_filter_display(base64_string):
    j = {'username': 'test088',
         'num_img': 1,
         'imgs': [base64_string],
         'procedure': 'histogram_eq',
         'img_format': 'JPG',
         'filename': 'airplane001.jpg'
         }
    r = requests.post(address + "/api/process_img", json=j)
    # print(r.text)
    r = r.json()
    imgs = r['processed_img']
    original_img = decode_b64(base64_string, 'JPG')
    decoded_img = decode_b64(imgs[0], 'JPG')
    figure, axes = plt.subplots(3, 2)
    original_histograms = r['original_histograms'][0]
    processed_histograms = r['processed_histograms'][0]
    # ax[0,0].imshow(original_img)
    # ax[0,1].imshow(decoded_img)
    # ax[1,0].plot(original_histograms[0], original_histograms[1])
    # ax[1,1].plot(processed_histograms[0], processed_histograms[1])
    for c, c_color in enumerate(('red', 'green', 'blue')):
        bins, img_hist = original_histograms[c_color]
        axes[c, 0].plot(bins, img_hist)
        axes[c, 0].set_ylabel(c_color)
    for c, c_color in enumerate(('red', 'green', 'blue')):
        bins, img_hist = processed_histograms[c_color]
        axes[c, 1].plot(bins, img_hist)
        axes[0, 1].set_title('Processed')
    plt.show()


def encode_b64(image):
    image_buf = io.BytesIO()
    mpimg.imsave(image_buf, image, format='JPG')
    image_buf.seek(0)
    b64_bytes = base64.b64encode(image_buf.read())
    return str(b64_bytes, encoding='utf-8')


def view_past_requests(username):
    r = requests.get(address + "/api/previous_request/" + username)
    print(r.json())


def retrieve_past_request(username, request_id):
    r = requests.get(address + "/api/retrieve_request/" +
                     username + '/' + request_id)
    r = r.json()
    originals = r['original_img']
    processed = r['processed_img']
    for i in range(len(originals)):
        fig, ax = plt.subplots(1, 2)
        img = decode_b64(originals[i], 'JPG')
        after_filtering = decode_b64(processed[i], 'JPG')
        ax[0].imshow(img)
        ax[1].imshow(after_filtering)
        plt.show()


def retrieve_metrics(username):
    r = requests.get(address + "/api/user_metrics/" + username)
    r = r.json()
    print(r)


if __name__ == '__main__':
    img_b64_string = read_file_as_b64("./images/airplane001.jpg")
    # local_load_filter_display(img_b64_string)

    # print(img_b64_string)
    # img = decode_b64(img_b64_string, 'JPG')
    # print(img.shape[0], img.shape[1])
    # reencoded_b64 = encode_b64(img)
    # print(reencoded_b64)
    # local_load_filter_display(img_b64_string)
    remote_filter_display(img_b64_string)
    # hist_equal_filter(img_b64_string)
    # save_b64_image(b64_string)

    # This section tests get requests
    # view_past_requests('test002222')
    # retrieve_past_request('test001', '4')
    # retrieve_metrics('test088')
