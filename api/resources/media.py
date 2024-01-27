import json
import subprocess

from apiflask import APIBlueprint, Schema, HTTPError
from apiflask.fields import String, List, Integer, Boolean, Nested
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError

from api.schemas.main import MediaSchema
from models.base import MediaModel, AlbumModel
from nguylinc_python_utils.misc import validate_ksuid

media_bp = APIBlueprint("Media", __name__, url_prefix="/media")


class AddMediaIn(Schema):
    # title = String()
    # thumbnail_path = String()
    media_url = String()
    # media_type = String()
    album_ids = List(String(validate=validate_ksuid))


@media_bp.post("/")
@media_bp.input(AddMediaIn, arg_name="params")
@media_bp.output(MediaSchema)
def add_media(params):
    # from api.app import session
    # media = MediaModel()
    # media.title = params["title"]
    # media.thumbnail_path = params["thumbnail_path"]
    # media.media_type = params["media_type"]
    # media.albums = []
    # for album_id in params["album_ids"]:
    #     album = session.query(AlbumModel).filter(AlbumModel.id == str(album_id)).first()
    #     media.albums.append(album)
    # session.add(media)
    # session.commit()
    # session.refresh(media)
    # return media.to_dict()

    command = f"yt-dlp --write-info-json --skip-download -o metadata --cookies ~/Desktop/cookies.txt \"{params['media_url']}\""
    process = subprocess.run(command, shell=True)
    if process.returncode == 0:
        # read files/metadata.json
        with open("metadata.info.json", "r") as f:
            metadata = json.load(f)

            id = metadata["id"]
            title = metadata["title"]
            thumbnail = metadata["thumbnail"]
            # description = metadata["description"]
            extractor_key = metadata["extractor_key"]
            uploader_id = metadata["uploader_id"]
            duration = metadata["duration"]
            webpage_url = metadata["webpage_url"]

            print(id)
            print(title)
            print(thumbnail)
            # print(description)
            print(extractor_key)
            print(uploader_id)
            print(duration)
            print(webpage_url)

            subprocess.run("rm metadata.info.json", shell=True)
    else:
        command = f"gallery-dl --no-download --dump-json --cookies ~/Desktop/cookies.txt \"{params['media_url']}\" > metadata.json"
        process = subprocess.run(command, shell=True)
        if process.returncode == 0:
            # read files/metadata.json
            with open("metadata.json", "r") as f:
                metadata = json.load(f)

                print(metadata)

                for image_obj in metadata:
                    # skip objects with length != 3
                    if len(image_obj) != 3:
                        continue
                    image_url = image_obj[1]
                    image_data = image_obj[2]
                    category = image_data["category"]

                    if category == "twitter":
                        image_data = image_obj[2]
                        author = image_data["author"]["name"]
                        tweet_id = image_data["tweet_id"]
                        webpage_url = f"https://twitter.com/{author}/status/{tweet_id}"
                        # content = image_data["content"]

                        print(image_url)
                        print(author)
                        print(webpage_url)
                        # print(content)
                    elif category == "instagram":
                        image_data = image_obj[2]
                        username = image_data["username"]
                        post_shortcode = image_data["post_shortcode"]
                        webpage_url = f"https://www.instagram.com/p/{post_shortcode}"
                        # description = image_data["description"]

                        print(image_url)
                        print(username)
                        print(webpage_url)
                        # print(description)
                    else:
                        raise HTTPError(422, "Unsupported photo website")

                subprocess.run("rm metadata.json", shell=True)
        else:
            raise HTTPError(400, "Invalid media URL")

    print(params)


class AddMediaToAlbumIn(Schema):
    media_id = String(validate=validate_ksuid)
    album_id = String(validate=validate_ksuid)


@media_bp.post("/add-to-album")
@media_bp.input(AddMediaToAlbumIn, arg_name="params")
@media_bp.output({})
def add_media_to_album(params):
    from api.app import session
    media = session.query(MediaModel).filter(MediaModel.id == str(params["media_id"])).first()
    album = session.query(AlbumModel).filter(AlbumModel.id == str(params["album_id"])).first()
    media.albums.append(album)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPError(400, "Media already in album")
    return {}


class RemoveMediaFromAlbumIn(Schema):
    media_id = String(validate=validate_ksuid)
    album_id = String(validate=validate_ksuid)


@media_bp.post("/remove-from-album")
@media_bp.input(RemoveMediaFromAlbumIn, arg_name="params")
@media_bp.output({})
def remove_media_from_album(params):
    from api.app import session
    media = session.query(MediaModel).filter(MediaModel.id == str(params["media_id"])).first()
    if not media:
        raise HTTPError(404, "Media not found")

    album = session.query(AlbumModel).filter(AlbumModel.id == str(params["album_id"])).first()
    if not album:
        raise HTTPError(404, "Album not found")

    media.albums.remove(album)
    session.commit()
    return {}


class GetMediaIn(Schema):
    media_id = String(validate=validate_ksuid)


@media_bp.get("/")
@media_bp.input(GetMediaIn, arg_name="params", location="query")
@media_bp.output(MediaSchema)
def get_media(params):
    from api.app import session
    media = session.query(MediaModel).filter(MediaModel.id == str(params["media_id"])).first()
    albums = [album.to_dict() for album in media.albums]
    return {**media.to_dict(), "albums": albums}


class QueryMediaIn(Schema):
    album_id = String(load_default=None, validate=validate_ksuid)
    last_id = String(load_default=None)
    limit = Integer(load_default=30)
    descending = Boolean(load_default=True)


class QueryMediaOut(Schema):
    media = List(Nested(MediaSchema))


@media_bp.get("/query")
@media_bp.input(QueryMediaIn, arg_name="params", location="query")
@media_bp.output(QueryMediaOut)
def query_media(params):
    from api.app import session
    q = session.query(MediaModel)
    if params["album_id"]:
        q = q.filter(MediaModel.albums.any(id=str(params["album_id"])))
    if params["last_id"]:
        if params["descending"]:
            q = q.filter(MediaModel.id < params["last_id"])
        else:
            q = q.filter(MediaModel.id > params["last_id"])
    if params["descending"]:
        q = q.order_by(desc(MediaModel.id))
    q = q.limit(params["limit"])

    if params["album_id"]:
        media_list = [media.to_dict() for media in q.all()]
    # if album was not specified, populate albums field of each media
    else:
        media_list = []
        for media in q.all():
            media_dict = media.to_dict()
            media_dict["albums"] = [album.to_dict() for album in media.albums]
            media_list.append(media_dict)

    # media_list = [media.to_dict() for media in q.all()]

    return {"media": media_list}


class DeleteMediaIn(Schema):
    media_ids = List(String(validate=validate_ksuid))


@media_bp.delete("/")
@media_bp.input(DeleteMediaIn, arg_name="params")
@media_bp.output({})
def delete_media(params):
    from api.app import session
    for media_id in params["media_ids"]:
        media = session.query(MediaModel).filter(MediaModel.id == str(media_id)).first()
        if not media:
            continue
        session.delete(media)
    session.commit()
    return {}
