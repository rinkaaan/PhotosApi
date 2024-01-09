from apiflask import APIBlueprint, Schema
from marshmallow.fields import String

from api.schemas.main import AlbumSchema
from models.base import AlbumModel

album_bp = APIBlueprint("Album", __name__, url_prefix="/album")


class AddAlbumIn(Schema):
    name = String()


@album_bp.post("/")
@album_bp.input(AddAlbumIn, arg_name="params")
@album_bp.output(AlbumSchema)
def add_album(params):
    from api.app import session
    album = AlbumModel()
    album.name = params["name"]
    session.add(album)
    session.commit()
    session.refresh(album)
    print(album.to_dict())
    return album.to_dict()
