run:=poetry run
package:=redes_2_audio_p2p

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