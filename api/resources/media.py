from apiflask import APIBlueprint, Schema
from apiflask.fields import String, UUID, List

from api.schemas.main import MediaSchema
from models.base import MediaModel, AlbumModel

media_bp = APIBlueprint("Media", __name__, url_prefix="/media")


class AddMediaIn(Schema):
    title = String()
    thumbnail_path = String()
    media_type = String()
    album_ids = List(UUID())


@media_bp.post("/")
@media_bp.input(AddMediaIn, arg_name="params")
@media_bp.output(MediaSchema)
def add_media(params):
    from api.app import session
    media = MediaModel()
    media.title = params["title"]
    media.thumbnail_path = params["thumbnail_path"]
    media.media_type = params["media_type"]
    media.albums = []
    for album_id in params["album_ids"]:
        album = session.query(AlbumModel).filter(AlbumModel.id == str(album_id)).first()
        media.albums.append(album)
    session.add(media)
    session.commit()
    session.refresh(media)
    return media.to_dict()


class AddMediaToAlbumIn(Schema):
    media_id = UUID()
    album_id = UUID()


@media_bp.post("/add-to-album")
@media_bp.input(AddMediaToAlbumIn, arg_name="params")
@media_bp.output(MediaSchema)
def add_media_to_album(params):
    from api.app import session
    media = session.query(MediaModel).filter(MediaModel.id == str(params["media_id"])).first()
    album = session.query(AlbumModel).filter(AlbumModel.id == str(params["album_id"])).first()
    media.albums.append(album)
    session.commit()
    session.refresh(media)
    return media.to_dict()


class GetMediaIn(Schema):
    media_id = UUID()


@media_bp.get("/")
@media_bp.input(GetMediaIn, arg_name="params", location="query")
@media_bp.output(MediaSchema)
def get_media(params):
    from api.app import session
    media = session.query(MediaModel).filter(MediaModel.id == str(params["media_id"])).first()
    albums = [album.to_dict() for album in media.albums]
    return {**media.to_dict(), "albums": albums}
