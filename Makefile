watch:
	mkdir -p dist/
	cp model.ttl dist/
	cp -r img dist/
	cp vocabularies/*.ttl dist/
	make build
	watchmedo shell-command \
		--patterns="*.adoc;*.css" \
		--ignore-directories \
		--recursive \
		--command='make build' \
		.

build:
	asciidoctor README.adoc -o dist/index.html
	asciidoctor editing.adoc -o dist/editing.html
	asciidoctor 00-master.adoc -o dist/model.html
	asciidoctor vocabularies/AnzAddressComponentTypes.adoc -o dist/AnzAddressComponentTypes.html
	asciidoctor vocabularies/AnzAddressLifecycleStageTypes.adoc -o dist/AnzAddressLifecycleStageTypes.html
	asciidoctor vocabularies/AnzAddressRoleTypes.adoc -o dist/AnzAddressRoleTypes.html
	asciidoctor vocabularies/AnzAddressStatusTypes.adoc -o dist/AnzAddressStatusTypes.html

http:
	httpwatcher --root dist \
		--host 127.0.0.1 \
		--port 8000 \
		--no-browser