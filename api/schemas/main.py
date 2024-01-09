from apiflask import Schema
from apiflask.fields import Integer, List, Nested, String, UUID, DateTime


class AlbumSchema(Schema):
    id = UUID()
    name = String()
    thumbnail_path = String()
    created_at = DateTime()
    updated_at = DateTime()


class MediaSchema(Schema):
    id = UUID()
    title = String()
    description = String()
    uploader = String()
    uploader_id = String()
    uploader_url = String()
    upload_date = String()
    tags = List(String())
    duration = Integer()
    webpage_url = String()
    extractor_key = String()
    # photo, video, audio
    media_type = String()
    thumbnail_path = String()
    media_path = String()
    width = Integer()
    height = Integer()
    # automatically create album for media's author, website source, media type (photo or video), and date (Jan 2024)
    albums = List(Nested(AlbumSchema))
    created_at = DateTime()
    updated_at = DateTime()