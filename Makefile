run:=poetry run
package:=redes_2_audio_p2p

init:
	pyenv install $(cat .python-version)
	poetry env use python
	$(MAKE) install

install:
	poetry install

run-server:
	@$(run) python -m $(package).exec.server

run-client:
	@$(run) python -m $(package).exec.client

fmt:
	$(run) black .

lint:
	$(run) pyflakes $(package)

test:
	$(run) pytest

inspect: fmt lint