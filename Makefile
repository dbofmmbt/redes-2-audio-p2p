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

wave-receiver:
	@$(run) python -m $(package).exec.wave-receiver

wave-sender:
	@$(run) python -m $(package).exec.wave-sender songs/test.wav

fmt:
	$(run) black .

lint:
	$(run) pyflakes $(package)

test:
	$(run) pytest

inspect: fmt lint