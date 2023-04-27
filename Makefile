run:=poetry run
package:=redes_2_audio_p2p

init:
	pyenv install $(cat .python-version)
	poetry env use python
	$(MAKE) install

install:
	poetry install

run:
	@$(run) python -m $(package)

fmt:
	$(run) black .

lint:
	$(run) pyflakes $(package)

test:
	$(run) pytest

inspect: fmt lint