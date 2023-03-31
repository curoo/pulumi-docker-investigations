# Based off of
# https://github.com/direnv/direnv/wiki/Python#poetry

layout_poetry() {
  _export_project_name
  _check_poetry_file_exists
  _sandbox_python_path
  _configure_poetry_for_venv
  _create_poetry_venv
  _activate_poetry_venv
}

_export_project_name() {
  export EXPEND_PROJECT=$(basename "$(pwd)")
}

_check_poetry_file_exists() {
  if [[ ! -f pyproject.toml ]]; then
    # shellcheck disable=SC2016
    log_error 'No pyproject.toml found. Use `poetry new` or `poetry init` to create one first.'
    exit 2
  fi
}

_sandbox_python_path() {
  THIS_PROJECT_UNDERSCORES=${EXPEND_PROJECT//-/_}
  PYTHONPATH="$(pwd)/${THIS_PROJECT_UNDERSCORES}"
  export PYTHONPATH
}

_configure_poetry_for_venv() {
  export POETRY_VIRTUALENVS_PATH="${HOME}/.venvs/pulumi-docker-investigations"
  export POETRY_VIRTUALENVS_CREATE=false
  VENV_NAME=$(basename "$(pwd)")
  VIRTUAL_ENV="${POETRY_VIRTUALENVS_PATH}/${VENV_NAME}"
  export VIRTUAL_ENV
}

_create_poetry_venv() {
  if [[ `which python3.9` && `which poetry` ]]; then
    if [ ! -d "${VIRTUAL_ENV}" ]; then
      python3.9 -m venv "${VIRTUAL_ENV}"
      poetry install
    fi
  else
    echo "Skipping python virtual environment setup"
  fi
}

_activate_poetry_venv() {
  if [ -d "${VIRTUAL_ENV}" ]; then
    source ${VIRTUAL_ENV}/bin/activate
  fi
}