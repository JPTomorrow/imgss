# Image To Sprite Sheet

A small library to take .png .jpeg .webm and .webp images and pack them into a sprite sheet atlas.


## Dependencies

```
pip install pillow pyinstaller
```

## USAGE

```
python atlas_generator.py /path/to/images /path/to/output output_atlas_name.png --sprite-width 32 --sprite-height 32 --width 4096 --height 4096
```

## Example Output
![test](./example_atlus/test-atlus.png)