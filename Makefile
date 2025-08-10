.PHONY: build clean install_dependencies deploy

build: install_dependencies
	rm -rf output
	billygoblog . -o output

build_server: build
	makeserver output -o server

install_dependencies:
	go install github.com/rubenvannieuwpoort/billygoblog@v0.0.5
	go install github.com/rubenvannieuwpoort/makeserver@v0.0.2

clean:
	rm -rf output

deploy: clean install_dependencies
	rm -rf output
	billygoblog . -o output
	GOOS=linux GOARCH=arm64 makeserver output -o server
	ssh -o StrictHostKeyChecking=no ruben@rubenvannieuwpoort.nl "mv /home/ruben/bin/server /home/ruben/bin/server.bak"
	scp -o StrictHostKeyChecking=no server ruben@rubenvannieuwpoort.nl:/home/ruben/bin/server
	ssh -o StrictHostKeyChecking=no ruben@rubenvannieuwpoort.nl "sudo systemctl restart server.service"
