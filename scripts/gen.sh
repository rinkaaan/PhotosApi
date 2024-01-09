WORKPLACE="$HOME/workplace/Photos"
WORKSPACE="$WORKPLACE/PhotosApi"

(
  cd "$WORKSPACE/api"
  flask spec --output openapi.yaml > /dev/null
)
