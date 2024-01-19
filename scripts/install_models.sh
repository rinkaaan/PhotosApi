WORKPLACE="$HOME/workplace/Photos"

(
  cd "$WORKPLACE/PhotosModels"
  pip install .
  rm -rf build
)
