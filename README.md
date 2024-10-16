# Llama Index with Google

# LlamaIndexGoogle
Llama Index with Google aims to provide unofficial snippets to be able to use Llama Index with Google's Alloy DB and Vertex AI LLM API and Embedding API calls.

```sh
## How to start
REPO_ROOT=$HOME/github/LlamaIndexGoogle
eval "$(pyenv init -)"
PY_BIN=3.12
set_python_alias ${PY_BIN}
pyenv shell ${PY_BIN}
VENV=${REPO_ROOT}/venv${PY_BIN//.}
python${PY_BIN} -m venv venv${PY_BIN//.}
curl https://bootstrap.pypa.io/get-pip.py | ${VENV}/bin/python
${VENV}/bin/pip install -r requirements.txt
${VENV}/bin/pip freeze | grep -v -f requirements.txt - | xargs ${VENV}/bin/pip uninstall -y
${VENV}/bin/python scriptXX.py # replace XX with num
```

## Script details

script1. Defines a way to use Embedding APIs
