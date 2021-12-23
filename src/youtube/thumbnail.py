import yaml
from PIL import Image, ImageDraw, ImageFont


def split_to_lines(text, draw, font, max_width):
    words = text.split()
    current = ''
    while words:
        new_words = []
        new_words.append(words.pop(0))
        while len(new_words[-1]) == 1 and words:
            new_words.append(words.pop(0))
        new_words = ' '.join(new_words)
        new_line = ' '.join([current, new_words]).strip()
        width = draw.textsize(new_line, font=font)[0]
        if width > max_width:
            yield current
            current = new_words
        else:
            current = new_line
    if current:
        yield current

        
def draw_box(img, d, context, get_font_path, scale):
    newimg = Image.new(
        'RGBA',
        (
            img.size[0] - d.get('x', 0),
            d.get('max-height', img.size[1] - d.get('y', 0)),
        )
    )

    draw = ImageDraw.Draw(newimg)
    cursor = 0
    for item in d['items']:
        if item.get('vskip'):
            cursor += int(round(item['vskip'] * scale))
        text = item['text'].format(**context)
        if not text:
            continue
        if item.get('uppercase'):
            text = text.upper()
        font = ImageFont.truetype(
            get_font_path(item['font-family']),
            int(round(item['font-size'] * scale)),
            layout_engine=ImageFont.LAYOUT_BASIC
        )
        max_width = item.get('max-width', newimg.size[0])

        for line in split_to_lines(text, draw, font, max_width):
            realheight = draw.textsize(line, font=font)[1]
            if cursor + realheight > newimg.size[1]:
                return False
            draw.text((0, cursor), line, font=font, fill=item.get('color'))
            cursor += int(round(item['line-height'] * scale))

    img.paste(newimg, (d.get('x', 0), d.get('y', 0)), newimg)
    return True


def draw_box_with_scaling(img, d, context, get_font_path):
    scale = 1.0
    while scale > 0:
        if draw_box(img, d, context, get_font_path, scale):
            return True
        scale -= 0.05
    


def create_thumbnail(background_path, defn, context, get_font_path):
    img = Image.open(background_path)
    d = yaml.safe_load(defn)
    for boxdef in d['boxes']:
        if not draw_box_with_scaling(img, boxdef, context, get_font_path):
            raise ValueError()
    return img
