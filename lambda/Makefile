FUNCTION_ARN := $(shell cd ../terraform && terraform output -raw lambda_function_arn)
ZIP := build/lambda_function.zip
PKG := build/packages.zip
SRC := $(shell ls *.py | grep -v ^test_)

.PHONY: all
all: $(ZIP) upload

.PHONY: clean
clean:
	rm -rf build package

build:
	mkdir -p build

requirements.txt: requirements.in
	pip-compile --output-file=$@ $^
	rm -rf package

package: requirements.txt
	mkdir -p package
	pip install -r requirements.txt --target ./package
	pip install --no-deps --target ./package pycognito

package-with-binaries-at-root: package
	find package/* -name \*.so -exec mv -f {} package/ \;

$(PKG): build package-with-binaries-at-root
	rm -f $@
	(cd package && zip -r ../$(PKG) .)

$(ZIP): build $(SRC) $(PKG)
	cp -f $(PKG) $@
	zip -r $@ $(SRC)

upload: $(ZIP)
	aws lambda update-function-code \
		--function-name $(FUNCTION_ARN) \
		--zip-file fileb://$^ \
	| cat

