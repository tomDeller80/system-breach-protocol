import utils.paths as paths
import pygame as pg
import json, os

class Storage:

    @staticmethod
    def load_image(filename, colorkey=None, scale=1):
        # Load an image from the packaged asset tree and optionally resize or tint-key it.
        fullname = Storage.get_storage_path(filename, is_static=True)
        image = pg.image.load(fullname)

        size = image.get_size()
        size = (size[0] * scale, size[1] * scale)
        image = pg.transform.scale(image, size)

        image = image.convert_alpha()
        if colorkey is not None:
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, pg.RLEACCEL)
        return image, image.get_rect()

    @staticmethod
    def load_sound(filename):
        # Return a pygame Sound object when the mixer is available.
        if not pg.mixer or not pg.mixer.get_init():
            return

        fullname = Storage.get_storage_path(filename, is_static=True)
        sound = pg.mixer.Sound(fullname)
        return sound

    @staticmethod
    def load_font(filename, font_size=24):
        # Fonts are treated like other packaged assets so the game can run from a bundle.
        if not pg.font or not pg.font.get_fonts():
            return

        fullname = Storage.get_storage_path(filename, is_static=True)
        font = pg.font.Font(fullname, font_size)
        return font


    @staticmethod
    def read_json(json_file, is_static=True):
        # Read static data from assets or mutable data from the app data folder.
        path = Storage.get_storage_path(json_file, is_static)

        try:
            with open(path, 'r') as f:
                data = json.load(f)

        except (FileNotFoundError, json.JSONDecodeError):

            if not is_static and json_file == "Score.json":
                return {"scores": []}

            raise FileNotFoundError(f"Required app data {json_file} missing.")

        return data

    @staticmethod
    def write_json(json_file, data):
        # Persist mutable state to the per-user app data directory.
        path = Storage.get_storage_path(json_file, is_static=False)

        try:
            with open(path, 'w') as f:
                json.dump(data, f, indent=4)
        except PermissionError:
            raise PermissionError(f"Insufficient permissions to write to file {json_file}")


    @staticmethod
    def get_storage_path(filename, is_static=True):
        # Split static packaged assets from writable runtime data.
        if is_static:
            return paths.get_resource_path(f"{filename}")
        else:
            return paths.get_app_data_path(filename)
