.PHONY: build install_dependencies

build:
	billygoblog . -o output
	makeserver output -o server

install_dependencies:
	go install github.com/rubenvannieuwpoort/billygoblog@v1.0.0
	go install github.com/rubenvannieuwpoort/makeserver@v1.0.0
