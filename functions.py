from PIL import Image


def load_quest_image(img_index, height=None, width=None, resize=1.0):
    path = f'imgs\\quests\\{int(img_index):03d}.png'
    img = Image.open(path)

    if height:
        ratio = img.height / (height*resize)
    elif width:
        ratio = img.width / (width*resize)
    else:
        return img
    new_dimensions = int(img.width // ratio), int(img.height // ratio)
    return img.resize(new_dimensions)


def load_icon_image(img_index, height=None, width=None, resize=1.0):
    img_index = 35 if not img_index else img_index
    path = f'imgs\\icons\\{int(img_index):03d}.png'
    img = Image.open(path)

    if height:
        ratio = img.height / (height*resize)
    elif width:
        ratio = img.width / (width*resize)
    else:
        return img
    new_dimensions = int(img.width // ratio), int(img.height // ratio)
    return img.resize(new_dimensions)


def get_img_color_avg(img):
    sum_r, sum_b, sum_g = 0, 0, 0
    count = 0
    for r, g, b in img.getdata():
        sum_r += r
        sum_g += g
        sum_b += b
        count += 1

    sum_r //= count
    sum_g //= count
    sum_b //= count

    return f'#{hex(sum_r*255*255 + sum_g*255 + sum_b)[2:]:0>6}'


def get_most_common_color(img, border_width=1):
    colors = {}
    color = 0
    width = img.width
    height = img.height
    for n, pixels in enumerate(img.getdata()):
        x, y = n % width, n // height
        if y < border_width or y >= width - border_width or x < border_width or x >= height - border_width:
            r, g, b = pixels
            c = r*256*256 + g*256 + b
            try:
                colors[c] += 1
            except KeyError:
                colors.update({c: 1})

    for c in sorted(colors.items(), key=lambda i: i[1], reverse=True):
        color = c[0]

        return f'#{hex(color)[2:]:0>6}'
