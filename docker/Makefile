.PHONY: build

build:
	time docker build \
		--build-arg BUILD_DATE=${BUILD_DATE} \
		--build-arg AUTOBAHN_TESTSUITE_VCS_REF=${AUTOBAHN_TESTSUITE_VCS_REF} \
		--build-arg AUTOBAHN_TESTSUITE_VERSION=${AUTOBAHN_TESTSUITE_VERSION} \
		-t crossbario/autobahn-testsuite \
		-t crossbario/autobahn-testsuite:${AUTOBAHN_TESTSUITE_VERSION} \
		-f Dockerfile .

version:
	docker run -it --rm crossbario/autobahn-testsuite python -V
	docker run -it --rm crossbario/autobahn-testsuite wstest --version

run:
	docker run -it --rm \
		-v ${PWD}/config:/config \
		-v ${PWD}/reports:/reports \
		-p 9001:9001 \
		--name fuzzingserver \
		crossbario/autobahn-testsuite

publish: build
	docker push crossbario/autobahn-testsuite:latest
	docker push crossbario/autobahn-testsuite:${AUTOBAHN_TESTSUITE_VERSION}

list:
	-docker images crossbario/autobahn-testsuite:*

clean:
	./removeall.sh
