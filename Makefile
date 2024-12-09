.PHONY: build install_dependencies

build:
	billygoblog . -o output
	makeserver output -o server

install_dependencies:
	go install github.com/rubenvannieuwpoort/billygoblog@v0.0.5
	go install github.com/rubenvannieuwpoort/makeserver@v0.0.2
