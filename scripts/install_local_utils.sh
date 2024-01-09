WORKPLACE="$HOME/workplace/Photos"

(
  cd "$WORKPLACE/PythonUtils"
  pip install .
  rm -rf build
)
