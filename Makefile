.PHONY: build deploy clean

build:
	rm -rf build
	python build.py

deploy: build
	ssh homeserver 'rm -rf /home/ruben/www.temp'
	rsync -a build/ homeserver:/home/ruben/www.temp
	ssh homeserver 'mkdir -p /home/ruben/www && atomic-exchange /home/ruben/www /home/ruben/www.temp && rm -rf /home/ruben/www.temp'

clean:
	rm -rf build
